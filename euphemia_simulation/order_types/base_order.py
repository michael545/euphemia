# Base Order Class
class Order:
    def __init__(self, order_id, bidding_zone, side):
        self.order_id = order_id
        self.bidding_zone = bidding_zone  # Represents a geographical area
        self.side = side  # 'buy' or 'sell'

    def __str__(self):
        return f"Order ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}"
