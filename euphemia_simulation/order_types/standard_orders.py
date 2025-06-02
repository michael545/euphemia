from .base_order import Order

# Example: Market Order
class MarketOrder(Order):
    def __init__(self, order_id, timestamp, quantity):
        super().__init__(order_id, timestamp, quantity, None) # Price is not set for market orders

    def __str__(self):
        return f"Market Order ID: {self.order_id}, Quantity: {self.quantity}"

# Example: Limit Order
class LimitOrder(Order):
    def __init__(self, order_id, timestamp, quantity, price_limit):
        super().__init__(order_id, timestamp, quantity, price_limit)
        self.price_limit = price_limit

    def __str__(self):
        return f"Limit Order ID: {self.order_id}, Quantity: {self.quantity}, Price Limit: {self.price_limit}"

# Example: Block Order
class BlockOrder(Order):
    # Block orders might have more complex conditions, e.g., all-or-none
    def __init__(self, order_id, timestamp, quantity, price, all_or_none=True):
        super().__init__(order_id, timestamp, quantity, price)
        self.all_or_none = all_or_none

    def __str__(self):
        return f"Block Order ID: {self.order_id}, Quantity: {self.quantity}, Price: {self.price}, All-or-None: {self.all_or_none}"
