# Main EUPHEMIA Simulation Runner
from core.cost_optimization import MarketClearing
from core.grid_simulation import Grid
# Assuming you have StepOrder, PiecewiseLinearOrder, BlockOrder, etc. defined in standard_orders
from order_types.standard_orders import StepOrder, PiecewiseLinearOrder, BlockOrder, MeritOrder, PUNOrder, ComplexOrder, ScalableComplexOrder


if __name__ == "__main__":
    print("EUPHEMIA entry running...")

    # 1. Define Bidding Zones
    bidding_zones = ["SI", "AT", "IT", "HU", "HR"]
    print(f"Bidding zones defined: {bidding_zones}")

    # 2. Define Interconnectors
    # Each interconnector is a dictionary specifying its properties.
    # 'id' is a unique  line itself.
    # 'coupling_model' can be 'ATC' or 'FlowBased'.
    # 'capacity_mw' is used for ATC.
    # For FlowBased, you'd typically have Critical Network Elements (CNEs) and their PTDFs/RAM, which is more complex.
    interconnectors = [
        # Slovenia (SI) - Austria (AT)
        {"id": "SI-AT-400kv-1", "from_zone": "SI", "to_zone": "AT", "capacity_mw": 500, "coupling_model": "ATC", "voltage_kv": 400},
        {"id": "SI-AT-400kv-2", "from_zone": "SI", "to_zone": "AT", "capacity_mw": 500, "coupling_model": "ATC", "voltage_kv": 400},
        {"id": "SI-AT-220kv-1", "from_zone": "SI", "to_zone": "AT", "capacity_mw": 300, "coupling_model": "ATC", "voltage_kv": 220},

        # Slovenia (SI) - Italy (IT)
        # Example: Assume Italy border is flowbased
        {"id": "SI-IT-400kv-1", "from_zone": "SI", "to_zone": "IT", "capacity_mw": 600, "coupling_model": "FlowBased", "voltage_kv": 400},
        {"id": "SI-IT-220kv-1", "from_zone": "SI", "to_zone": "IT", "capacity_mw": 250, "coupling_model": "FlowBased", "voltage_kv": 220},

        # (SI) - Hungary (HU)
        {"id": "SI-HU-400kv-1", "from_zone": "SI", "to_zone": "HU", "capacity_mw": 400, "coupling_model": "ATC", "voltage_kv": 400},

        # SI) - Croatia (HR)
        {"id": "SI-HR-400kv-1", "from_zone": "SI", "to_zone": "HR", "capacity_mw": 450, "coupling_model": "ATC", "voltage_kv": 400},
        {"id": "SI-HR-220kv-1", "from_zone": "SI", "to_zone": "HR", "capacity_mw": 200, "coupling_model": "ATC", "voltage_kv": 220},

        # (AT) - Italy (IT)
        # SI-IT
        {"id": "AT-IT-400kv-1", "from_zone": "AT", "to_zone": "IT", "capacity_mw": 700, "coupling_model": "FlowBased", "voltage_kv": 400},

        # super simple for now, the model is focused on SI and neighbors + AT-IT .
        {"id": "AT-HU-400kv-1", "from_zone": "AT", "to_zone": "HU", "capacity_mw": 500, "coupling_model": "ATC", "voltage_kv": 400},
        {"id": "IT-HR-DC-1", "from_zone": "IT", "to_zone": "HR", "capacity_mw": 200, "coupling_model": "ATC", "voltage_kv": 0}, # Example DC link

    ]
    print(f"Interconnectors defined: {len(interconnectors)}")

    # 3. Initialize Grid
    grid = Grid(bidding_zones, interconnectors)
    print(f"Grid initialized with {len(grid.bidding_zones)} zones and {len(grid.interconnectors)} interconnectors.")

    # 4. Create some dummy orders
    # (Using StepOrder as an example, replace with other types as needed)
    orders = [
        StepOrder(order_id="B_SI_001", bidding_zone="SI", side="buy", price=50, quantity=100, period=1),
        StepOrder(order_id="S_SI_001", bidding_zone="SI", side="sell", price=45, quantity=80, period=1),
        StepOrder(order_id="B_AT_001", bidding_zone="AT", side="buy", price=55, quantity=120, period=1),
        StepOrder(order_id="S_IT_001", bidding_zone="IT", side="sell", price=40, quantity=200, period=1),
        # Add more orders for different zones and periods
    ]
    print(f"Created {len(orders)} sample orders.")

    market_clearing_algo = MarketClearing(grid)

    # 6. Run the Optimization (Market Clearing)
    accepted_orders, clearing_price_per_zone = market_clearing_algo.optimize(orders)
    # Note: clearing_price might become a dictionary {zone: price} in a multi-zone setup

    # 7. Check Grid Constraints (Simplified)
    # In a real simulation, flows would be derived from accepted orders and net positions.
    # This requires a more complex calculation based on market clearing results.
    # For now, we'll call it with dummy net_positions or skip if it's too complex at this stage.
    # net_positions_example = {("SI", "AT"): 50} # Example: 50MW flow from SI to AT
    # grid.check_constraints(net_positions_example)

    # 8. Calculate Social Welfare
    # This will also need to be adapted for multi-zone clearing prices.
    # For now, let's assume a single representative clearing price for simplicity or adapt the function.
    # If clearing_price_per_zone is a dict, calculate_social_welfare needs to handle it.
    example_clearing_price_for_welfare = 50 # Placeholder
    if isinstance(clearing_price_per_zone, dict) and bidding_zones[0] in clearing_price_per_zone:
        example_clearing_price_for_welfare = clearing_price_per_zone[bidding_zones[0]]
    elif isinstance(clearing_price_per_zone, (int, float)):
        example_clearing_price_for_welfare = clearing_price_per_zone

    social_welfare = market_clearing_algo.calculate_social_welfare(accepted_orders, example_clearing_price_for_welfare)

    print("\n--- Simulation Summary ---")
    if isinstance(clearing_price_per_zone, dict):
        for zone, price in clearing_price_per_zone.items():
            print(f"Clearing Price for {zone}: {price}")
    else:
        print(f"Clearing Price (system-wide placeholder): {clearing_price_per_zone}")
    print(f"Number of Accepted Orders: {len(accepted_orders)}")
    # for order in accepted_orders:
    # print(f"  - {order}")
    print(f"social welfare score: {social_welfare}")

    print("==++EUPHEMIA SIM DONE.++==\n" )
