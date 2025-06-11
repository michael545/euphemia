# Cost Function definition /cost funct.  == social welfare calculation
class MarketClearing:
    def __init__(self, grid):
        self.grid = grid

    def optimize(self, orders):
        print("optimizzing welfare...")
        # just dummy logic for now
        accepted_orders = orders
        clearing_price = 100 
        print(f"Market cleared with {len(accepted_orders)} orders at price {clearing_price}")
        return accepted_orders, clearing_price

    def calculate_social_welfare(self, accepted_orders, clearing_price):
        # (consumer surplus + producer surplus + congestion rent)
        print("Calculating social welfare...")
        consumer_surplus = 0
        producer_surplus = 0
        # ultra simplified for now, 
        for order in accepted_orders:
            if order.price is not None: #limit orders
                if order.quantity > 0: #Buy order
                    if order.price >= clearing_price:
                        consumer_surplus += (order.price - clearing_price) * order.quantity
                else: # avtomatsko sell order
                    if order.price <= clearing_price:
                        producer_surplus += (clearing_price - order.price) * abs(order.quantity)
        
        
        # Congestion rent = f(price difference * flow)
    
        congestion_rent = 0 
        
        total_welfare = consumer_surplus + producer_surplus + congestion_rent
        print(f"Consumer Surplus: {consumer_surplus}, Producer Surplus: {producer_surplus}, Congestion Rent: {congestion_rent}")
        print(f"Total welfare: {total_welfare}")
        return total_welfare
