# Base Order Class
class Order:
    def __init__(self, order_id, bidding_zone, side, period):
        self.order_id = order_id
        self.bidding_zone = bidding_zone  # geographical area for which one single price is determined
        self.side = side  # 'buy' or 'sell'
        self.period = period # Integer from 0 to 23 representing the hour

    def __str__(self):
        return f"Order ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, Period: {self.period}"
