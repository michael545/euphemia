# Base Order Class
class Order:
    def __init__(self, order_id, timestamp, quantity, price):
        self.order_id = order_id
        self.timestamp = timestamp
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return f"Order ID: {self.order_id}, Quantity: {self.quantity}, Price: {self.price}"
