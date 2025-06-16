# Cost Function definition /cost funct.  == social welfare calculation
import pulp

class MarketClearing:
    def __init__(self, grid, hourly_constraints):
        self.grid = grid
        self.hourly_constraints = hourly_constraints

    def optimize(self, orders_by_period):
        """
        Optimizes market clearing for all 24 hourly periods.

        Args:
            orders_by_period (dict): A dictionary where keys are period numbers (0-23)
                                     and values are lists of Order objects for that period.

        Returns:
            A tuple: (all_accepted_orders_by_period, all_clearing_prices_by_period, all_interconnector_flows_by_period)
            - all_accepted_orders_by_period (dict): {period: [accepted_orders]}
            - all_clearing_prices_by_period (dict): {period: {zone: price}}
            - all_interconnector_flows_by_period (dict): {period: {ic_id: flow}}
        """
        print("Starting multi-period welfare optimization...")
        all_accepted_orders_by_period = {}
        all_clearing_prices_by_period = {} # {period: {zone: price}}
        all_interconnector_flows_by_period = {} # {period: {ic_id: flow}}
        
        # Store net positions for ramping constraints between periods
        # {zone: [np_h0, np_h1, ..., np_h23]}
        net_positions_per_zone_all_periods = {zone: [0.0] * 24 for zone in self.grid.bidding_zones}
        # Store interconnector flows for ramping constraints
        # {ic_id: [flow_h0, flow_h1, ..., flow_h23]}
        interconnector_flows_all_periods = {ic['id']: [0.0] * 24 for ic in self.grid.interconnectors}


        for period in range(24):
            print(f"\\n--- Optimizing for Period {period} ---")
            orders_current_period = orders_by_period.get(period, [])
            if not orders_current_period:
                print(f"No orders for period {period}. Skipping.")
                all_accepted_orders_by_period[period] = []
                all_clearing_prices_by_period[period] = {zone: 0 for zone in self.grid.bidding_zones} # Or some default
                all_interconnector_flows_by_period[period] = {ic['id']: 0 for ic in self.grid.interconnectors}
                continue

            # Create a new LP problem for each period
            prob = pulp.LpProblem(f"Welfare_Optimization_Period_{period}", pulp.LpMaximize)

            # Decision Variables
            # Order acceptance: 0 or 1 for each order (simplified for now, assumes orders are fully accepted or rejected)
            # For block orders, this is appropriate. For step orders, we'd need continuous variables for accepted quantity.
            # This will be a major simplification for now.
            accepted_vars = pulp.LpVariable.dicts("Accepted", 
                                                  [order.order_id for order in orders_current_period], 
                                                  cat='Binary')

            # Net export for each zone (can be positive or negative)
            # net_export_vars = pulp.LpVariable.dicts("NetExport", 
            #                                         self.grid.bidding_zones, 
            #                                         lowBound=-100000, # Arbitrary large number
            #                                         upBound=100000,  # Arbitrary large number
            #                                         cat='Continuous')
            
            # Interconnector flows (positive for from_zone -> to_zone, negative for reverse)
            # flow_vars = pulp.LpVariable.dicts("Flow",
            #                                   [ic['id'] for ic in self.grid.interconnectors],
            #                                   lowBound=-100000, # Placeholder
            #                                   upBound=100000,   # Placeholder
            #                                   cat='Continuous')


            # Objective Function: Maximize Social Welfare
            # Simplified: sum of (price * quantity_accepted) for sell orders (negative quantity)
            # and sum of (price * quantity_accepted) for buy orders (positive quantity)
            # This is a proxy for producer and consumer surplus relative to a clearing price.
            # A more accurate formulation would involve dual variables (prices).
            # For now, we maximize based on declared order prices.
            
            # --- Objective Function: Maximize Social Welfare ---
            # This formulation assumes that the "price" in the order is the value for the buyer
            # or the cost for the seller.
            objective = pulp.lpSum([
                accepted_vars[order.order_id] * order.price * order.quantity # quantity is negative for sell
                if hasattr(order, 'price') and hasattr(order, 'quantity') and order.price is not None and order.quantity is not None
                else 0 
                for order in orders_current_period
            ])
            prob += objective
            
            # --- Constraints ---
            # 1. Power Balance for each zone: sum of accepted generation = sum of accepted demand + net export
            # This is complex with the current order structure.
            # Simplified: For each zone, sum of (accepted_quantity for buy orders) + sum of (accepted_quantity for sell orders) + net_export = 0
            # Let's simplify further for now and assume net_export is implicitly handled by flows.

            # For each zone, sum of quantities of accepted orders must equal net export from that zone.
            # And sum of all net exports must be zero.
            # prob += pulp.lpSum([net_export_vars[zone] for zone in self.grid.bidding_zones]) == 0, "Overall_Power_Balance"

            # for zone in self.grid.bidding_zones:
            #     prob += pulp.lpSum([
            #         accepted_vars[order.order_id] * order.quantity 
            #         if hasattr(order, 'quantity') and order.quantity is not None and order.bidding_zone == zone
            #         else 0
            #         for order in orders_current_period
            #     ]) == net_export_vars[zone], f"Power_Balance_{zone}"


            # 2. Interconnector Capacity Constraints (ATC)
            # for ic in self.grid.interconnectors:
            #     if ic['coupling_model'] == 'ATC':
            #         net_available_cap = self.hourly_constraints.get_net_available_capacity(ic['id'], period)
            #         # Flow definition: Positive flow from 'from_zone' to 'to_zone'
            #         # flow_vars[ic['id']] is the variable representing this flow.
            #         prob += flow_vars[ic['id']] <= net_available_cap, f"ATC_Max_Flow_{ic['id']}"
            #         prob += flow_vars[ic['id']] >= -net_available_cap, f"ATC_Min_Flow_{ic['id']}" # Assuming symmetric capacity for now

            # 3. Flow definition based on net exports (Kirchhoff's Current Law for zones)
            # For each zone, sum of flows out of the zone must equal net_export_vars[zone]
            # for zone in self.grid.bidding_zones:
            #     outgoing_flows = pulp.lpSum([
            #         flow_vars[ic['id']] for ic in self.grid.interconnectors if ic['from_zone'] == zone
            #     ])
            #     incoming_flows = pulp.lpSum([
            #         flow_vars[ic['id']] for ic in self.grid.interconnectors if ic['to_zone'] == zone
            #     ])
            #     prob += net_export_vars[zone] == outgoing_flows - incoming_flows, f"Zone_Flow_Balance_{zone}"
            
            # 4. Ramping Constraints for Interconnectors
            # if period > 0:
            #     for ic_id in interconnector_flows_all_periods.keys():
            #         prev_flow = interconnector_flows_all_periods[ic_id][period-1]
            #         ramp_up_limit, ramp_down_limit = self.hourly_constraints.get_interconnector_ramping_limits(ic_id, period)
                        
            #         prob += flow_vars[ic_id] - prev_flow <= ramp_up_limit, f"RampUp_{ic_id}_P{period}"
            #         prob += prev_flow - flow_vars[ic_id] <= ramp_down_limit, f"RampDown_{ic_id}_P{period}" # ramp_down_limit is positive value

            # 5. Net Position Delta Constraints for Bidding Zones
            # if period > 0:
            #     for zone in self.grid.bidding_zones:
            #         prev_np = net_positions_per_zone_all_periods[zone][period-1]
            #         delta_up_limit, delta_down_limit = self.hourly_constraints.get_zone_net_position_delta_limits(zone, period)
                        
            #         # net_export_vars is export, so positive delta_up means more export or less import
            #         # net_export_vars[zone] - prev_np <= delta_up_limit
            #         # prev_np - net_export_vars[zone] <= delta_down_limit
                        
            #         prob += net_export_vars[zone] - prev_np <= delta_up_limit, f"NP_DeltaUp_{zone}_P{period}"
            #         prob += prev_np - net_export_vars[zone] <= delta_down_limit, f"NP_DeltaDown_{zone}_P{period}"


            # For now, let's use a simplified approach without PuLP for the first pass to get structure right.
            # This will be a placeholder for the actual optimization.
            # The actual implementation will require a proper solver (like CBC, GLPK, Gurobi, CPLEX)
            # and PuLP or a similar library.

            print(f"  Running simplified clearing for period {period} (placeholder)...")
            # Placeholder: Accept all orders, no real clearing price or flow calculation yet.
            accepted_orders_for_period = [order for order in orders_current_period if hasattr(order, 'price') and order.price is not None] # Basic filter
            
            # Dummy clearing prices (e.g., average price or a fixed value)
            # This needs to be derived from the dual variables of the power balance constraints in a real LP.
            clearing_prices_for_period = {zone: 100.0 for zone in self.grid.bidding_zones} # Placeholder

            # Dummy interconnector flows
            interconnector_flows_for_period = {ic['id']: 0.0 for ic in self.grid.interconnectors} # Placeholder

            # Store results for this period
            all_accepted_orders_by_period[period] = accepted_orders_for_period
            all_clearing_prices_by_period[period] = clearing_prices_for_period
            all_interconnector_flows_by_period[period] = interconnector_flows_for_period
            
            # Update net positions and flows for next period's ramping (using placeholders for now)
            # for zone in self.grid.bidding_zones:
            #     current_period_np = 0 # Calculate from accepted_orders_for_period if possible
            #     net_positions_per_zone_all_periods[zone][period] = current_period_np
            # for ic_id in interconnector_flows_all_periods.keys():
            #     interconnector_flows_all_periods[ic_id][period] = interconnector_flows_for_period[ic_id]


            # TODO: Replace above simplified logic with PuLP solver invocation
            # Example (conceptual, needs full variable and constraint setup):
            # prob.solve(pulp.PULP_CBC_CMD(msg=0))
            # print(f"  Status for period {period}: {pulp.LpStatus[prob.status]}")

            # if pulp.LpStatus[prob.status] == 'Optimal':
            #     accepted_orders_for_period = []
            #     for order in orders_current_period:
            #         if accepted_vars[order.order_id].varValue > 0.5: # If binary variable is 1
            #             accepted_orders_for_period.append(order)
                
            #     # Clearing prices are the duals of the zonal power balance constraints
            #     # clearing_prices_for_period = {
            #     #     zone: prob.constraints[f"Power_Balance_{zone}"].pi 
            #     #     for zone in self.grid.bidding_zones
            #     # }
            #     # For now, using a placeholder as duals are not straightforward without full setup
            #     clearing_prices_for_period = {zone: 100.0 for zone in self.grid.bidding_zones}


            #     interconnector_flows_for_period = {
            #         ic['id']: flow_vars[ic['id']].varValue for ic in self.grid.interconnectors
            #     }

            #     all_accepted_orders_by_period[period] = accepted_orders_for_period
            #     all_clearing_prices_by_period[period] = clearing_prices_for_period
            #     all_interconnector_flows_by_period[period] = interconnector_flows_for_period

            #     # Update net positions and flows for next period's ramping
            #     for zone in self.grid.bidding_zones:
            #         net_positions_per_zone_all_periods[zone][period] = net_export_vars[zone].varValue
            #     for ic_id in interconnector_flows_all_periods.keys():
            #         interconnector_flows_all_periods[ic_id][period] = flow_vars[ic_id].varValue
            # else:
            #     print(f"  Optimization failed or was infeasible for period {period}.")
            #     all_accepted_orders_by_period[period] = []
            #     all_clearing_prices_by_period[period] = {zone: 0 for zone in self.grid.bidding_zones}
            #     all_interconnector_flows_by_period[period] = {ic['id']: 0 for ic in self.grid.interconnectors}


        print("\\nCompleted multi-period optimization simulation.")
        return all_accepted_orders_by_period, all_clearing_prices_by_period, all_interconnector_flows_by_period

    def calculate_social_welfare(self, accepted_orders_by_period, clearing_prices_by_period, interconnector_flows_by_period):
        """
        Calculates total social welfare across all periods.

        Args:
            accepted_orders_by_period (dict): {period: [accepted_orders]}
            clearing_prices_by_period (dict): {period: {zone: price}}
            interconnector_flows_by_period (dict): {period: {ic_id: flow}}

        Returns:
            float: Total social welfare.
        """
        total_social_welfare_all_periods = 0
        print("\\n--- Calculating Social Welfare for All Periods ---")

        for period in range(24):
            accepted_orders = accepted_orders_by_period.get(period, [])
            clearing_prices_for_zone = clearing_prices_by_period.get(period, {})
            
            if not accepted_orders:
                # print(f"Period {period}: No accepted orders, welfare contribution is 0.")
                continue

            period_consumer_surplus = 0
            period_producer_surplus = 0

            for order in accepted_orders:
                if not hasattr(order, 'price') or not hasattr(order, 'quantity') or \
                   order.price is None or order.quantity is None:
                    continue # Skip orders without price/quantity

                zone_price = clearing_prices_for_zone.get(order.bidding_zone)
                if zone_price is None:
                    # print(f"Warning: No clearing price for zone {order.bidding_zone} in period {period}. Skipping order {order.order_id} for welfare calc.")
                    continue
                
                # Assuming order.quantity > 0 for buy, < 0 for sell
                if order.side.lower() == 'buy': # Buy order
                    if order.price >= zone_price:
                        period_consumer_surplus += (order.price - zone_price) * order.quantity
                elif order.side.lower() == 'sell': # Sell order
                    # order.quantity is negative for sell orders in standard_orders.py
                    # order.price is the minimum price the seller wants.
                    if order.price <= zone_price:
                         # (clearing_price - seller_price) * abs(quantity)
                        period_producer_surplus += (zone_price - order.price) * abs(order.quantity)
            
            # Congestion Rent for the period
            # Sum over interconnectors: flow * (price_to_zone - price_from_zone)
            period_congestion_rent = 0
            flows_this_period = interconnector_flows_by_period.get(period, {})
            for ic_id, flow_value in flows_this_period.items():
                interconnector = next((ic for ic in self.grid.interconnectors if ic['id'] == ic_id), None)
                if not interconnector:
                    continue

                price_from_zone = clearing_prices_for_zone.get(interconnector['from_zone'])
                price_to_zone = clearing_prices_for_zone.get(interconnector['to_zone'])

                if price_from_zone is not None and price_to_zone is not None:
                    # Positive flow is from 'from_zone' to 'to_zone'
                    # Congestion rent is flow * (price_destination - price_origin)
                    # If flow > 0, rent = flow * (price_to_zone - price_from_zone)
                    # If flow < 0 (meaning from to_zone to from_zone), let actual_flow = -flow.
                    # rent = actual_flow * (price_from_zone - price_to_zone)
                    # rent = (-flow) * (price_from_zone - price_to_zone) = flow * (price_to_zone - price_from_zone)
                    # So the formula holds.
                    period_congestion_rent += flow_value * (price_to_zone - price_from_zone)
            
            period_total_welfare = period_consumer_surplus + period_producer_surplus + period_congestion_rent
            # print(f"Period {period}: CS={period_consumer_surplus:.2f}, PS={period_producer_surplus:.2f}, CR={period_congestion_rent:.2f}, Total={period_total_welfare:.2f}")
            total_social_welfare_all_periods += period_total_welfare

        print(f"\\nTotal Social Welfare (all periods): {total_social_welfare_all_periods:.2f}")
        return total_social_welfare_all_periods
