import graphviz

def generate_grid_visualization(bidding_zones, interconnectors, output_filename="grid_visualization", output_format="pdf"):
    
    dot = graphviz.Digraph('ElectricityGrid', comment='European Electricity Grid Model')
    dot.attr(rankdir='LR', size='10,10', overlap='false', splines='true', sep='+15') # Added sep for more spacing

    # Add nodes (bidding zones)
    for zone_data in bidding_zones: # Iterate through the list of zone dictionaries
        zone_name = zone_data.get('name') if isinstance(zone_data, dict) else None # Safely get the 'name' attribute
        if zone_name:
            dot.node(zone_name, zone_name, shape='ellipse', style='filled', fillcolor='lightblue')
        else:
            print(f"Warning: Bidding zone data item {str(zone_data)[:100]} is missing a 'name' key or is not a dictionary. Skipping node creation.")

    # edges
    for ic in interconnectors:
        from_zone = ic['from_zone']
        to_zone = ic['to_zone']
        
        # label
        label = f"ID: {ic.get('id', 'N/A')}\n"
        label += f"Capacity: {ic.get('capacity_mw', 'N/A')} MW\n"
        label += f"Model: {ic.get('coupling_model', 'N/A')}"
        if 'voltage_kv' in ic:
            label += f"\nVoltage: {ic.get('voltage_kv')} kV"

        # edge based on coupling model
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

    print("visualizing_grid.py executed directly (for testing/example purposes).")
    print("To generate visualization from the main simulation, run main_sim_entry.py.")
    
    # print("standalone visualization with example data...")
    # example_zones = ["TestZone1", "TestZone2"]
    # example_ics = [
    #     {"id": "TZ1-TZ2-01", "from_zone": "TestZone1", "to_zone": "TestZone2", "capacity_mw": 100, "coupling_model": "ATC", "voltage_kv": 400}
    # ]
    # generate_grid_visualization(example_zones, example_ics, output_filename="standalone_test_grid")
    pass