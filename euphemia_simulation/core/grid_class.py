# Grid SIMulation 
class Grid:
    def __init__(self, bidding_zones, interconnectors):
        self.bidding_zones = bidding_zones  
        self.interconnectors = interconnectors  

    def calculate_ptdf(self, critical_network_elements=None):
        print("Calculating PTDF (placeholder)...")
        # IDEA: return a dictionary mapping CNEs to PTDF vectors/mats
        # e.g., {'CNE1': {'ZoneA_export': 0.3, 'ZoneB_export': -0.2, ...}}
        return {}

    def get_ram(self, critical_network_elements=None):
        # a dict mapping CNEs to their RAM values
        # e.g., {'CNE1': 500 MW, 'CNE2': 300 MW}
        return {}

    def get_interconnector_capacity(self, from_zone, to_zone):
        """
        helper to get total ATC capacity between two zones for a *(Real world capacity can be directional)*.
        """
        total_capacity = 0
        for ic in self.interconnectors:
            if ic['coupling_model'] == 'ATC':
                if ic['from_zone'] == from_zone and ic['to_zone'] == to_zone:
                    total_capacity += ic['capacity_mw']
                # mby later for directionnal capacity as well, add another check
                # elif ic['from_zone'] == to_zone and ic['to_zone'] == from_zone:
                #     total_capacity += ic['capacity_mw'] # Or a different capacity for reverse direction
        return total_capacity
