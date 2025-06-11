from .base_order import Order

# 2.2. Aggregated Period Orders
class StepOrder(Order):
    """Represents a simple limit order."""
    def __init__(self, order_id, bidding_zone, side, price, quantity, period):
        super().__init__(order_id, bidding_zone, side)
        self.price = price  # The limit price for the order (€/MWh)
        self.quantity = quantity  # The volume of the order (MWh)
        self.period = period  # The specific market time unit for which the order is valid

    def __str__(self):
        return f"StepOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, Price: {self.price}, Quantity: {self.quantity}, Period: {self.period}"

class PiecewiseLinearOrder(Order):
    """Represents an interpolated order that is accepted gradually over a price range."""
    def __init__(self, order_id, bidding_zone, side, price_start, price_end, quantity, period):
        super().__init__(order_id, bidding_zone, side)
        self.price_start = price_start # The price at which the order starts to be accepted
        self.price_end = price_end # The price at which the order is fully accepted
        self.quantity = quantity # The total volume of the order (MWh)
        self.period = period # The specific market time unit for which the order is valid

    def __str__(self):
        return f"PiecewiseLinearOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, PriceStart: {self.price_start}, PriceEnd: {self.price_end}, Quantity: {self.quantity}, Period: {self.period}"

# 2.3. Block Orders
class BlockOrder(Order):
    """These are orders that span one or more periods and have special acceptance conditions."""
    def __init__(self, order_id, bidding_zone, side, price, profile, min_acceptance_ratio=1.0, is_flexible=False, exclusive_group_id=None, parent_block=None):
        super().__init__(order_id, bidding_zone, side)
        self.price = price # A single price limit for the entire block
        self.profile = profile # A dict mapping each period in the block to a specific vol
        self.min_acceptance_ratio = min_acceptance_ratio # min acceptance (1.0 for fill-or-kill)
        self.is_flexible = is_flexible # True if the algorithm chooses the best period (single-period block)
        self.exclusive_group_id = exclusive_group_id # Identifier for Exclusive Group
        self.parent_block = parent_block # Reference to parent BlockOrder in a Linked Block Orders family
        self.child_blocks = [] # List of child BlockOrder objects

    def __str__(self):
        return f"BlockOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, Price: {self.price}, MAR: {self.min_acceptance_ratio}, Flexible: {self.is_flexible}"

# 2.4. Complex Orders
class ComplexOrder(Order):
    """These are sets of orders that are subject to a single, overarching condition."""
    def __init__(self, order_id, bidding_zone, side, sub_orders, fixed_term=0.0, variable_term=0.0, increase_gradient=None, decrease_gradient=None, scheduled_stop_periods=None):
        super().__init__(order_id, bidding_zone, side)
        self.sub_orders = sub_orders # Collection of curve sub-orders (e.g., StepOrder objects)
        # MIC/MP Condition Attributes
        self.fixed_term = fixed_term # Fixed cost/payment component in Euros
        self.variable_term = variable_term # Variable cost/payment component in €/MW per accepted unit
        # Load gradient changes 
        self.increase_gradient = increase_gradient # Max allowed increase in matched volume period to period
        self.decrease_gradient = decrease_gradient # Max allowed decrease in matched volume period to period
        # Scheduled Stop Attributes
        self.scheduled_stop_periods = scheduled_stop_periods if scheduled_stop_periods else [] # array of periods for shutdown

    def __str__(self):
        return f"ComplexOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, SubOrders: {len(self.sub_orders)}, FixedTerm: {self.fixed_term}"

# 2.5. Scalable Complex Orders
class ScalableComplexOrder(ComplexOrder):
    """A variation of Complex Orders with slightly different economic conditions."""
    def __init__(self, order_id, bidding_zone, side, sub_orders, fixed_term, min_acceptance_powers, increase_gradient=None, decrease_gradient=None, scheduled_stop_periods=None):
        # Note: ScalableComplexOrder only has fixed_term, not variable_term for its primary economic condition.
        super().__init__(order_id, bidding_zone, side, sub_orders, fixed_term=fixed_term, variable_term=0.0, increase_gradient=increase_gradient, decrease_gradient=decrease_gradient, scheduled_stop_periods=scheduled_stop_periods)
        self.min_acceptance_powers = min_acceptance_powers # Profile of min power per period for activation

    def __str__(self):
        return f"ScalableComplexOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, SubOrders: {len(self.sub_orders)}, FixedTerm: {self.fixed_term}"

# 2.6. Merit Orders
class MeritOrder(StepOrder):
    """Special step orders used for ranking."""
    def __init__(self, order_id, bidding_zone, side, price, quantity, period, merit_order_number):
        super().__init__(order_id, bidding_zone, side, price, quantity, period)
        self.merit_order_number = merit_order_number # Unique number for ranking at-the-money orders

    def __str__(self):
        return f"MeritOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, Price: {self.price}, MON: {self.merit_order_number}"
# 2.7. PUNOrder (Discontinued)
'''
used to be for the Italian market, but nnow since Jan 2025 it's dicontinued "Prezzo Unico Nazionale" PUN
'''
# class PUNOrder(MeritOrder):
#     """A special type of demand merit order used in the Italian market."""
#     # Cleared at national PUN price instead of zonal price - this logic would be in the clearing algorithm.
#     def __init__(self, order_id, bidding_zone, side, price, quantity, period, merit_order_number):
#         super().__init__(order_id, bidding_zone, side, price, quantity, period, merit_order_number)

#     def __str__(self):
#         return f"PUNOrder ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, Price: {self.price}, MON: {self.merit_order_number}"

print("Orders loads with no mistakes.") 