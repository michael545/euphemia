# Main EUPHEMIA Simulation Runner
from core.cost_optimization import MarketClearing
from core.grid_simulation import Grid
from order_types.standard_orders import LimitOrder, MarketOrder


if __name__ == "__main__":
    print("Starting EUPHEMIA Simulation Example...")

    # 1. Define the Grid
    # Example: 2 nodes (Market Areas) and 1 transmission line between them
    nodes = ["Area1", "Area2"]
    lines = [{"from": "Area1", "to": "Area2", "capacity": 100}] # 100 MW capacity
    grid = Grid(nodes, lines)
    print(f"Grid initialized with {len(nodes)} nodes and {len(lines)} lines.")

    # 2. simulate some orders
    orders = [
        LimitOrder(order_id="B001", timestamp="T1", quantity=50, price_limit=120), # Buy 50 MWh if price <= 120
        LimitOrder(order_id="S001", timestamp="T1", quantity=-40, price_limit=90), # Sell 40 MWh if price >= 90
        MarketOrder(order_id="B002", timestamp="T2", quantity=30), # Buy 30 MWh at market price
        LimitOrder(order_id="S002", timestamp="T2", quantity=-60, price_limit=95), # Sell 60 MWh if price >= 95
    ]
    print(f"Created {len(orders)} sample orders.")


    market_clearing_algo = MarketClearing(grid)

    # 4. Run the Optimization (Market Clearing)
    accepted_orders, clearing_price = market_clearing_algo.optimize(orders)

    # 5. Check Grid Constraints (Simplified)
    # In a real simulation, flows would be derived from accepted orders and net positions
    # For simplicity, we'll assume flows are manageable for now.
    # flows_example = {"Area1_to_Area2": 20} # Example flow
    # grid.check_constraints(flows_example)

    # 6. Calculate Social Welfare
    social_welfare = market_clearing_algo.calculate_social_welfare(accepted_orders, clearing_price)

    print("\n--- Simulation Summary ---")
    print(f"Clearing Price: {clearing_price}")
    print(f"Number of Accepted Orders: {len(accepted_orders)}")
    # for order in accepted_orders:
    # print(f"  - {order}")
    print(f"Calculated Social Welfare: {social_welfare}")

    print("\nEUPHEMIA Simulation Example Finished.")
