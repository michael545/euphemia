import graphviz

def generate_grid_visualization(bidding_zones, interconnectors, output_filename="grid_visualization", output_format="pdf"):
    """visual graphviz graph of the grid initialized in main.

    Args:
        bidding_zones (list): A list of bidding zone names.
        interconnectors (list): A list of dictionaries, where each dictionary
                                represents an interconnector with keys like
                                'from_zone', 'to_zone', 'id', 'capacity_mw',
                                'coupling_model'.
        output_filename (str): The name of the output file (without extension).
        output_format (str): The format of the output file (e.g., 'pdf', 'png').
    """
    dot = graphviz.Digraph('ElectricityGrid', comment='European Electricity Grid Model')
    dot.attr(rankdir='LR', size='10,10', overlap='false', splines='true', sep='+15') # Added sep for more spacing

    # Add nodes (bidding zones)
    for zone in bidding_zones:
        dot.node(zone, zone, shape='ellipse', style='filled', fillcolor='lightblue')

    # Add edges (interconnectors)
    for ic in interconnectors:
        from_zone = ic['from_zone']
        to_zone = ic['to_zone']
        
        # Prepare label
        label = f"ID: {ic.get('id', 'N/A')}\n"
        label += f"Capacity: {ic.get('capacity_mw', 'N/A')} MW\n"
        label += f"Model: {ic.get('coupling_model', 'N/A')}"
        if 'voltage_kv' in ic:
            label += f"\nVoltage: {ic.get('voltage_kv')} kV"

        # Customize edge based on coupling model
        color = "black"
        style = "solid"
        penwidth = "1.5"
        if ic.get('coupling_model') == 'FlowBased':
            color = "blue"
            style = "dashed"
            penwidth = "2.0"
        elif ic.get('coupling_model') == 'ATC':
            color = "darkgreen"
        
        dot.edge(from_zone, to_zone, label=label, color=color, style=style, penwidth=penwidth)

    try:
        dot.render(output_filename, format=output_format, view=True, cleanup=True)
        print(f"Grid visualization saved as {output_filename}.{output_format} and opened.")
    except graphviz.backend.execute.ExecutableNotFound:
        print("Graphviz executable not found. Please ensure Graphviz is installed and in your system's PATH.")
        print(f"Diagram source saved as {output_filename}.gv")
        dot.save(f"{output_filename}.gv")
    except Exception as e:
        print(f"An error occurred during rendering: {e}")
        print(f"Diagram source saved as {output_filename}.gv")
        dot.save(f"{output_filename}.gv")


if __name__ == "__main__":
    # This block is now primarily for demonstrating standalone use or testing.
    # The main simulation will call generate_grid_visualization directly.
    print("visualizing_grid.py executed directly (for testing/example purposes).")
    print("To generate visualization from the main simulation, run main_sim_entry.py.")
    
    # Example data for standalone testing (optional, can be removed if not needed)
    # If you want to test visualize_grid.py independently, you can uncomment and use this:
    # print("Running standalone visualization with example data...")
    # example_zones = ["TestZone1", "TestZone2"]
    # example_ics = [
    #     {"id": "TZ1-TZ2-01", "from_zone": "TestZone1", "to_zone": "TestZone2", "capacity_mw": 100, "coupling_model": "ATC", "voltage_kv": 400}
    # ]
    # generate_grid_visualization(example_zones, example_ics, output_filename="standalone_test_grid")
    pass # Or remove the __main__ block if no standalone execution is desired.