class Order:
    def __init__(self, order_id, bidding_zone, side, period):
        self.order_id = order_id
        self.bidding_zone = bidding_zone  
        self.side = side  # 'buy' /'sell'
        self.period = period #0 # 0th hour to 23/ 23rd hour

    def __str__(self):
        return f"Order ID: {self.order_id}, Zone: {self.bidding_zone}, Side: {self.side}, Period: {self.period}"
