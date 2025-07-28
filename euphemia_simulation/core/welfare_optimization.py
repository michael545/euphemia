from ortools.linear_solver import pywraplp
from order_types.standard_orders import StepOrder, PiecewiseLinearOrder, BlockOrder, MeritOrder, ComplexOrder, ScalableComplexOrder

class MarketClearing:
    def __init__(self, grid, hourly_constraints):
        self.grid = grid
        self.hourly_constraints = hourly_constraints
        self.num_periods = 24 
    def optimize(self, periodic_orders, block_orders, complex_orders):
        """
        Optimizes market clearing for all 24 hourly periods at once.
        builds a single Mixed-Integer Programming (MIP) problem.

        Args:
            periodic_orders (dict): {period: [Order objects]} for single-period orders.
            block_orders (list): A list of all BlockOrder objects.
            complex_orders (list): A list of all ComplexOrder and ScalableComplexOrder objects.
        
        Returns:
            A tuple: (all_accepted_orders, all_clearing_prices, all_interconnector_flows)
        """
        print("single multi-period welfare optimization")

        solver = pywraplp.Solver.CreateSolver('SCIP')    
        infinity = solver.infinity()

        
        # For step/piecewise orders,  model the accepted quantity as a continuous variable.
        accepted_periodic_qty = {} 
        for period, orders in periodic_orders.items():
            for order in orders:
                # We model accepted quantity as a continuous variable between 0 and the order's quantity
                # Assuming quantity is positive for buy and negative for sell
                if order.side == 'buy':
                    accepted_periodic_qty[order.order_id] = solver.NumVar(0, order.quantity, f"AcceptedQty_{order.order_id}")
                else: # sell
                    accepted_periodic_qty[order.order_id] = solver.NumVar(order.quantity, 0, f"AcceptedQty_{order.order_id}")

        # bool  to represent the accept/reject decision.
        accepted_block_vars = {order.order_id: solver.BoolVar(f"Accept_{order.order_id}") for order in block_orders}
        accepted_complex_vars = {order.order_id: solver.BoolVar(f"Accept_{order.order_id}") for order in complex_orders}

        # --- network vars ---
        net_position = {} # {zone: {period: var}}
        for zone in self.grid.bidding_zones:
            net_position[zone] = {}
            for p in range(self.num_periods):
               #positive (import) or negative (export)
                net_position[zone][p] = solver.NumVar(-infinity, infinity, f"NP_{zone}_p{p}")
        
        interconnector_flow = {} # {ic_id: {period: var}}
        for ic in self.grid.interconnectors:
            interconnector_flow[ic['id']] = {}
            for p in range(self.num_periods):
                # Flow can be positive (from->to) or negative (to->from)
                interconnector_flow[ic['id']][p] = solver.NumVar(-infinity, infinity, f"Flow_{ic['id']}_p{p}")
        
        print(f"Defined {len(solver.variables())} variables for the optimization problem.")

        # --- 3. Define the Objective Function: Maximize Social Welfare ---
        objective = solver.Objective()
        
        # Add welfare from periodic orders
        for period, orders in periodic_orders.items():
            for order in orders:
                # Note: quantity is negative for sell orders, so this correctly subtracts cost.
                objective.SetCoefficient(accepted_periodic_qty[order.order_id], order.price)

        # Add welfare from block orders
        for order in block_orders:
            for period, quantity in order.profile.items():
                # += welfare contribution is price * quantity * binary_acceptance_variable
                objective.SetCoefficient(accepted_block_vars[order.order_id], order.price * quantity)

        # Add welfare from complex orders (and their sub-orders)
        for order in complex_orders:
            for sub_order in order.sub_orders:
                # The welfare contribution of each sub-order is tied to the main complex order's acceptance
                # A constraint will link them. Here we just define the objective part.
                # Create a temporary variable for the accepted quantity of the sub-order
                accepted_sub_qty_var = solver.NumVar(sub_order.quantity if sub_order.side == 'sell' else 0, 
                                                     sub_order.quantity if sub_order.side == 'buy' else 0, 
                                                     f"AcceptedSubQty_{sub_order.order_id}")
                objective.SetCoefficient(accepted_sub_qty_var, sub_order.price)
                # Link this sub-order's acceptance to the main complex order's binary variable
                solver.Add(accepted_sub_qty_var <= accepted_complex_vars[order.order_id] * (sub_order.quantity if sub_order.side == 'buy' else 1e5)) # Large M for upper bound
                solver.Add(accepted_sub_qty_var >= accepted_complex_vars[order.order_id] * (sub_order.quantity if sub_order.side == 'sell' else -1e5)) # Large M for lower bound

        objective.SetMaximization()
        print("Objective function defined.")

        power_balance_constraints = {} # store for dual val. (price) extraction

        # -- Power Balance(for each zone, for each period) --
        # Sum(sells) - Sum of withdrawals (buys) = Net Export
        for zone in self.grid.bidding_zones:
            power_balance_constraints[zone] = {}
            for p in range(self.num_periods):
                zonal_balance_expr = solver.Sum([
                    accepted_periodic_qty[o.order_id]
                    for o in periodic_orders.get(p, []) if o.bidding_zone == zone
                ])
                # Add block order contributions for this period
                for bo in block_orders:
                    if p in bo.profile and bo.bidding_zone == zone:
                        zonal_balance_expr += accepted_block_vars[bo.order_id] * bo.profile[p]
                
                # Add complex order contributions for this period
                # This part needs the temporary variables created in the objective section
                for co in complex_orders:
                    for sub in co.sub_orders:
                        if sub.period == p and co.bidding_zone == zone:
                             # Find the corresponding sub-quantity variable created earlier
                            sub_qty_var = next((v for v in solver.variables() if v.name() == f"AcceptedSubQty_{sub.order_id}"), None)
                            if sub_qty_var:
                                zonal_balance_expr += sub_qty_var

                # Constraint: Sum of order quantities = Net Position
                # Note: OR-Tools constraints are typically written as LHS - RHS = 0 or <= 0 etc.
                constraint = solver.Constraint(0, 0, f"PowerBalance_{zone}_p{p}")
                constraint.SetCoefficient(zonal_balance_expr, 1)
                constraint.SetCoefficient(net_position[zone][p], -1)
                power_balance_constraints[zone][p] = constraint

        # -- Flow Balance Constraint (for each zone, for each period) --
        # Net Position = Sum of Outgoing Flows - Sum of Incoming Flows
        for zone in self.grid.bidding_zones:
            for p in range(self.num_periods):
                flow_balance_expr = 0
                for ic in self.grid.interconnectors:
                    if ic['from_zone'] == zone:
                        flow_balance_expr += interconnector_flow[ic['id']][p]
                    elif ic['to_zone'] == zone:
                        flow_balance_expr -= interconnector_flow[ic['id']][p]
                solver.Add(net_position[zone][p] == flow_balance_expr, f"FlowBalance_{zone}_p{p}")

        # -- Interconnector ATC, ramping -
        for ic in self.grid.interconnectors:
            for p in range(self.num_periods):
                capacity = self.hourly_constraints.get_net_available_capacity(ic['id'], p)
                solver.Add(interconnector_flow[ic['id']][p] <= capacity, f"ATC_Max_{ic['id']}_p{p}")
                # symmetric capacity.this may not reflect real life
                solver.Add(interconnector_flow[ic['id']][p] >= -capacity, f"ATC_Min_{ic['id']}_p{p}")

                # Ramping Constraint (for periods p > 0)
                if p > 0:
                    ramp_up, ramp_down = self.hourly_constraints.get_interconnector_ramping_limits(ic['id'], p)
                    delta_flow = interconnector_flow[ic['id']][p] - interconnector_flow[ic['id']][p-1]
                    solver.Add(delta_flow <= ramp_up, f"RampUp_{ic['id']}_p{p}")
                    solver.Add(delta_flow >= -ramp_down, f"RampDown_{ic['id']}_p{p}") # ramp_down is positive
        
        # -- Zonal Net Position Ramping Constraints --
        for zone in self.grid.bidding_zones:
            for p in range(self.num_periods):
                if p > 0:
                    delta_np, delta_down = self.hourly_constraints.get_zone_net_position_delta_limits(zone, p)
                    delta_np_expr = net_position[zone][p] - net_position[zone][p-1]
                    solver.Add(delta_np_expr <= delta_np, f"NP_DeltaUp_{zone}_p{p}")
                    solver.Add(delta_np_expr >= -delta_down, f"NP_DeltaDown_{zone}_p{p}")
        
        # -- TODO:  constraints for advanced orders like MIC, Load Gradient etc.
        # Example for a MIC on a Complex Order (Simplified - real MIC requires duals)
        # for co in complex_orders:
        #    if hasattr(co, 'fixed_term'):
        #       # forces rejection if not profitable enough. complex in real life.
        #       # Placeholder constraint:
        #       total_revenue_expr = solver.Sum(...) # Sum of sub-order revenues
        #       total_cost_expr = co.fixed_term + solver.Sum(...) # Sum of sub-order costs
        #       solver.Add(total_revenue_expr >= accepted_complex_vars[co.order_id] * total_cost_expr)
        
        print(f"Defined {len(solver.constraints())} constraints.")
        print("Starting the solver...")

        # SOLVER
        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print(f"Optimization successful! Objective value (Total Welfare): {objective.Value():.2f}")
            
            # results dicts 
            all_accepted_orders = {p: [] for p in range(self.num_periods)}
            all_clearing_prices = {p: {} for p in range(self.num_periods)}
            all_interconnector_flows = {p: {} for p in range(self.num_periods)}

            # periodic order results
            for p, orders in periodic_orders.items():
                for order in orders:
                    accepted_qty = accepted_periodic_qty[order.order_id].solution_value()
                    
                    if abs(accepted_qty) > 1e-6:
             
                        order.accepted_quantity = accepted_qty # Add a temporary attribute
                        all_accepted_orders[p].append(order)
            
            # lock and complex order results
            for bo in block_orders:
                if accepted_block_vars[bo.order_id].solution_value() > 0.5:
                     for p in bo.profile:
                        all_accepted_orders[p].append(bo) # add the block order to each period it's active in
            
            for co in complex_orders:
                if accepted_complex_vars[co.order_id].solution_value() > 0.5:
                    for sub in co.sub_orders:
                        all_accepted_orders[sub.period].append(sub) # add accepted sub-orders
            
            # getprices (duals) and flows
            for p in range(self.num_periods):
                for zone in self.grid.bidding_zones:
                    all_clearing_prices[p][zone] = -power_balance_constraints[zone][p].dual_value()
                
                for ic in self.grid.interconnectors:
                    all_interconnector_flows[p][ic['id']] = interconnector_flow[ic['id']][p].solution_value()

            return all_accepted_orders, all_clearing_prices, all_interconnector_flows

        else:
            print("Optimization failed or no solutin possible")
            return {}, {}, {}