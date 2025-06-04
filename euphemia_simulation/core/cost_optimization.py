# Cost Function definition / Market Clearing cost function social welfare calculation

class MarketClearing:
    def __init__(self, grid):
        self.grid = grid

    def optimize(self, orders):
        # This is the core of EUPHEMIA, aiming to maximize social welfare
        print("Optimizing market clearing...")
        
        # HAHAHA just dummy logic for now
        accepted_orders = orders
        clearing_price = 100 # Placeholder clearing price
        
        print(f"Market cleared with {len(accepted_orders)} orders at price {clearing_price}")
        return accepted_orders, clearing_price

    def calculate_social_welfare(self, accepted_orders, clearing_price):
        # Placeholder for social welfare calculation
        # (consumer surplus + producer surplus + congestion rent)
        print("Calculating social welfare...")
        consumer_surplus = 0
        producer_surplus = 0
        # This is a very simplified calculation
        for order in accepted_orders:
            if order.price is not None: #limit orders
                if order.quantity > 0: # Buy order
                    if order.price >= clearing_price:
                        consumer_surplus += (order.price - clearing_price) * order.quantity
                else: # avtomatsko sell order
                    if order.price <= clearing_price:
                        producer_surplus += (clearing_price - order.price) * abs(order.quantity)
        
        
        # Congestion rent would require flow calculations and price differences between zones
        congestion_rent = 0 
        
        total_welfare = consumer_surplus + producer_surplus + congestion_rent
        print(f"Consumer Surplus: {consumer_surplus}, Producer Surplus: {producer_surplus}, Congestion Rent: {congestion_rent}")
        print(f"Total welfare: {total_welfare}")
        return total_welfare
