# Main EUPHEMIA Simulation Runner
from euphemia_simulation.core.welfare_optimization import MarketClearing
from euphemia_simulation.core.grid_class import Grid 
from euphemia_simulation.core.hourly_grid_constraints import HourlyGridConstraints 
from euphemia_simulation.order_types.standard_orders import StepOrder, PiecewiseLinearOrder, BlockOrder, MeritOrder, ComplexOrder, ScalableComplexOrder 
from euphemia_simulation.visualizing_grid import generate_grid_visualization


if __name__ == "__main__":
    print("EUPHEMIA entry running...")
    # 1. Bidding Zones
    bidding_zones = ["SI", "AT", "IT", "HU", "HR"]
    print(f"Bidding zones defined: {bidding_zones}")

  
    # FAKE scenario
    default_aac_profile = [10] * 24 # Example: 10 MW AAC for all hours
    default_ramping_up = 50 #  50 MW/h up-ramping limit
    default_ramping_down = 50 #: same for down Abs(-50 MW/h)
    interconnectors = [
        {"id": "SI-AT-400kv-1", "from_zone": "SI", "to_zone": "AT", "capacity_mw": 500, "coupling_model": "ATC", "voltage_kv": 400, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        {"id": "SI-AT-400kv-2", "from_zone": "SI", "to_zone": "AT", "capacity_mw": 500, "coupling_model": "ATC", "voltage_kv": 400, "aac_profile": [15]*24, "ramping_up_limit_mw_per_hour": 60, "ramping_down_limit_mw_per_hour": 60},
        {"id": "SI-AT-220kv-1", "from_zone": "SI", "to_zone": "AT", "capacity_mw": 300, "coupling_model": "ATC", "voltage_kv": 220, "aac_profile": [5]*24, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        
        {"id": "SI-IT-400kv-1", "from_zone": "SI", "to_zone": "IT", "capacity_mw": 600, "coupling_model": "FlowBased", "voltage_kv": 400, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": 70, "ramping_down_limit_mw_per_hour": 70}, # Ramping still relevant for FB CNEs
        {"id": "SI-IT-220kv-1", "from_zone": "SI", "to_zone": "IT", "capacity_mw": 250, "coupling_model": "FlowBased", "voltage_kv": 220, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        
        {"id": "SI-HU-400kv-1", "from_zone": "SI", "to_zone": "HU", "capacity_mw": 400, "coupling_model": "ATC", "voltage_kv": 400, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        
        {"id": "SI-HR-400kv-1", "from_zone": "SI", "to_zone": "HR", "capacity_mw": 450, "coupling_model": "ATC", "voltage_kv": 400, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        {"id": "SI-HR-220kv-1", "from_zone": "SI", "to_zone": "HR", "capacity_mw": 200, "coupling_model": "ATC", "voltage_kv": 220, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        
        {"id": "AT-IT-400kv-1", "from_zone": "AT", "to_zone": "IT", "capacity_mw": 700, "coupling_model": "FlowBased", "voltage_kv": 400, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": 80, "ramping_down_limit_mw_per_hour": 80},
        
        {"id": "AT-HU-400kv-1", "from_zone": "AT", "to_zone": "HU", "capacity_mw": 500, "coupling_model": "ATC", "voltage_kv": 400, "aac_profile": default_aac_profile, "ramping_up_limit_mw_per_hour": default_ramping_up, "ramping_down_limit_mw_per_hour": default_ramping_down},
        {"id": "IT-HR-DC-1", "from_zone": "IT", "to_zone": "HR", "capacity_mw": 200, "coupling_model": "ATC", "voltage_kv": 10000, "aac_profile": [0]*24, "ramping_up_limit_mw_per_hour": 200, "ramping_down_limit_mw_per_hour": 200}, # DC lines can ramp fast
    ]
    print(f"Interconnectors defined: {len(interconnectors)}")

    # 2b. Define Zonal Net Position Delta Limits
    # Example: SI can't change its net position by more than 100MW up or down in any given hour.
    # These would typically come from TSO specifications.
    zone_np_delta_limits = {
        "SI": {"up_profile": [100] * 24, "down_profile": [100] * 24},
        "AT": {"up_profile": [150] * 24, "down_profile": [150] * 24},
        "IT": {"up_profile": [200] * 24, "down_profile": [200] * 24},
        "HU": {"up_profile": [80] * 24, "down_profile": [80] * 24},
        "HR": {"up_profile": [70] * 24, "down_profile": [70] * 24},
    }
    print(f"Zonal Net Position delta limits defined for {len(zone_np_delta_limits)} zones.")

    # 3. grid_init
    grid = Grid(bidding_zones, interconnectors) # static topology
    print(f"Grid initialized with {len(grid.bidding_zones)} zones and {len(grid.interconnectors)} interconnectors.")
    
    hourly_constraints = HourlyGridConstraints(bidding_zones, interconnectors, zone_np_delta_limits)
    print("HourlyGridConstraints done.")

    print("Generating grid visualization from main_sim_entry.py...")
    generate_grid_visualization(bidding_zones, interconnectors, output_filename="euphemia_grid_from_main")

    # 4list of orders for multiple periods
    aggregated_orders_list = {}

    #H0 Orders
    aggregated_orders_list[0] = [
        StepOrder(order_id="B_SI_001_h0", bidding_zone="SI", side="buy", price=50, quantity=100, period=0),
        StepOrder(order_id="S_SI_001_h0", bidding_zone="SI", side="sell", price=45, quantity=-80, period=0), # Quantity negative for sell
        StepOrder(order_id="B_AT_001_h0", bidding_zone="AT", side="buy", price=55, quantity=120, period=0),
        StepOrder(order_id="S_IT_001_h0", bidding_zone="IT", side="sell", price=40, quantity=-200, period=0),
        MeritOrder(order_id="M_SI_001_h0", bidding_zone="SI", side="sell", price=45, quantity=-10, period=0, merit_order_number=1),
        PiecewiseLinearOrder(order_id="PL_AT_001_h0", bidding_zone="AT", side="buy", price_start=48, price_end=52, quantity=50, period=0)
    ]

    # H1 Orders
    aggregated_orders_list[1] = [
        StepOrder(order_id="B_SI_001_h1", bidding_zone="SI", side="buy", price=52, quantity=90, period=1),
        StepOrder(order_id="S_AT_001_h1", bidding_zone="AT", side="sell", price=48, quantity=-150, period=1),
        StepOrder(order_id="B_IT_001_h1", bidding_zone="IT", side="buy", price=58, quantity=180, period=1),
    ]

    # Idea: BlockOrders go to the list of orders for one of their periods,
    # For simplicity in this data structure, we can add it to period 0,
    block_order_1 = BlockOrder(
        order_id="Block_SI_001_h0-2",
        bidding_zone="SI",
        side="buy",
        price=47, # 1 price for the entire block
        profile={0: 30, 1: 30, 2: 30}, # Quantity per period
        min_acceptance_ratio=1.0 # Fill-or-kill
    )
    if 0 not in aggregated_orders_list: aggregated_orders_list[0] = []
    aggregated_orders_list[0].append(block_order_1)

    # This order's sub_orders are for period 0 and 1
    complex_sub_orders_1 = [
        StepOrder(order_id="CSO1_SI_h0", bidding_zone="SI", side="sell", price=40, quantity=-20, period=0),
        StepOrder(order_id="CSO1_SI_h1", bidding_zone="SI", side="sell", price=42, quantity=-25, period=1)
    ]
    complex_order_1 = ComplexOrder(
        order_id="Complex_SI_MIC_001",
        bidding_zone="SI",
        side="sell",
        sub_orders=complex_sub_orders_1,
        fixed_term=100, # e.g., MIC 100 EUR if accepted
        variable_term=0 # No extra MWh income requirement beyond sub-order prices
    )
    if 0 not in aggregated_orders_list: aggregated_orders_list[0] = []
    aggregated_orders_list[0].append(complex_order_1)

    # Scalable Complex Order - example
    scalable_sub_orders_1 = [
        StepOrder(order_id="SCSO1_AT_h0", bidding_zone="AT", side="sell", price=35, quantity=-50, period=0),
        StepOrder(order_id="SCSO1_AT_h1", bidding_zone="AT", side="sell", price=38, quantity=-60, period=1)
    ]
    scalable_complex_order_1 = ScalableComplexOrder(
        order_id="Scalable_AT_001",
        bidding_zone="AT",
        side="sell",
        sub_orders=scalable_sub_orders_1,
        fixed_term=50, # Fixed income if activated
        min_acceptance_powers={0: 10, 1: 15} # Min power (MW) per period for activation
    )
    if 0 not in aggregated_orders_list: aggregated_orders_list[0] = []
    aggregated_orders_list[0].append(scalable_complex_order_1)
    
    # Period 2 Orders (example, can be expanded)
    aggregated_orders_list[2] = [
        StepOrder(order_id="S_HU_001_h2", bidding_zone="HU", side="sell", price=46, quantity=-70, period=2),
        StepOrder(order_id="B_HR_001_h2", bidding_zone="HR", side="buy", price=53, quantity=60, period=2),
    ]
    

    total_orders = sum(len(orders) for orders in aggregated_orders_list.values())
    print(f"Created a total of {total_orders} sample orders across {len(aggregated_orders_list)} periods.")

    market_clearing_algo = MarketClearing(grid, hourly_constraints) # 
    print("MarketClearing algorithm initialized.")

    # 6. RUn the algo (Market Clearing)
    accepted_orders_result, clearing_prices_result, interconnector_flows_result = market_clearing_algo.optimize(aggregated_orders_list)
    
    print(f"Optimization finished.")
    if accepted_orders_result:
        for period, orders in accepted_orders_result.items():
            print(f"  Period {period}: Accepted {len(orders)} orders.")
    if clearing_prices_result:
        for period, prices in clearing_prices_result.items():
            print(f"  Period {period}: Clearing Prices: {prices}")
    if interconnector_flows_result:
        for period, flows in interconnector_flows_result.items():
            print(f"  Period {period}: Interconnector Flows: {flows}")

    print("\\nEUPHEMIA Simulation Example Finished.")
