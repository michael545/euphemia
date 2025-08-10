class HourlyGridConstraints:
    def __init__(self, bidding_zones_data, interconnectors_data, zone_np_delta_limits_data):
        """
        Manages grid limits for a 1h of the next 24h.

        Args:
            bidding_zones_data (list): List of bidding zone names.
            interconnectors_data (list): List of interconnector dictionaries.
                Each interconnector dict is expected to have:
                - 'id': Unique interconnector ID.
                - 'from_zone': Origin bidding zone.
                - 'to_zone': Destination bidding zone.
                - 'capacity_mw': Max physical capacity (used for ATC).
                - 'coupling_model': 'ATC' or 'FlowBased'.
                - 'aac_profile': List of 24 hourly Already Allocated Capacities (MW).
                - 'ramping_up_limit_mw_per_hour': Max positive change in flow (MW/h). Can be a single value or a list of 24.
                - 'ramping_down_limit_mw_per_hour': Max negative change in flow (MW/h) (absolute value). Can be a single value or a list of 24.
            zone_np_delta_limits_data (dict): Maps zone names to their net position delta limits.
                e.g., {'SI': {'up_profile': [50]*24, 'down_profile': [50]*24}}
        """
        self.bidding_zones = bidding_zones_data
        # ICs by ID for easy lookup
        self.interconnectors = {ic['id']: ic for ic in interconnectors_data}
        self.zone_np_delta_limits = zone_np_delta_limits_data

        # validation of profiles
        for ic_id, ic_data in self.interconnectors.items():
            if not isinstance(ic_data.get('aac_profile'), list) or len(ic_data['aac_profile']) != 24:
                raise ValueError(f"Interconnector {ic_id} 'aac_profile' must be a list of 24 hourly values.")
            
            for ramp_key in ['ramping_up_limit_mw_per_hour', 'ramping_down_limit_mw_per_hour']:
                ramp_val = ic_data.get(ramp_key)
                if ramp_val is not None and isinstance(ramp_val, list) and len(ramp_val) != 24:
                    raise ValueError(f"Interconnector {ic_id} '{ramp_key}' profile must be a list of 24 hourly values if it's a list.")

        for zone_id, limits_data in self.zone_np_delta_limits.items():
            if not isinstance(limits_data.get('up_profile'), list) or len(limits_data['up_profile']) != 24:
                raise ValueError(f"Zone {zone_id} 'up_profile' for NP delta limits must be a list of 24 hourly values.")
            if not isinstance(limits_data.get('down_profile'), list) or len(limits_data['down_profile']) != 24:
                raise ValueError(f"Zone {zone_id} 'down_profile' for NP delta limits must be a list of 24 hourly values.")

    def get_net_available_capacity(self, interconnector_id, hour_index):
        """interconnector capcatiy getter for a given hour (0-23)."""
        if not (0 <= hour_index <= 23):
            raise ValueError("hour_index must be between 0 and 23.")
        
        ic = self.interconnectors.get(interconnector_id)
        if not ic:
            raise ValueError(f"Interconnector {interconnector_id} not found.")

        if ic['coupling_model'] == 'ATC':
            physical_capacity = ic['capacity_mw']
            aac = ic['aac_profile'][hour_index]
            return max(0, physical_capacity - aac)
        elif ic['coupling_model'] == 'FlowBased':
            print(f"Warning: get_net_available_capacity called for FlowBased IC {interconnector_id}. This is a simplification.")
            # simulation purposes, if you need a placeholder, it could be its nominal capacity,, not how FB works
            return ic['capacity_mw'] 
        else:
            raise ValueError(f"Unknown coupling model for interconnector {interconnector_id}")

    def get_interconnector_ramping_limits(self, interconnector_id, hour_index):
        """Gets ramping limits (up_limit, down_limit) for an interconnector for a given hour (0-23)."""
        if not (0 <= hour_index <= 23): # ramping means *to* this hour from previous
            raise ValueError("hour_index must be between 0 and 23.")
        
        ic = self.interconnectors.get(interconnector_id)
        if not ic:
            raise ValueError(f"Interconnector {interconnector_id} not found.")

        up_limit_val = ic.get('ramping_up_limit_mw_per_hour', float('inf')) # default to no limit
        down_limit_val = ic.get('ramping_down_limit_mw_per_hour', float('inf')) # default to no limit

        # limits are profiles (lists) or single vals
        if isinstance(up_limit_val, list):
            up_limit = up_limit_val[hour_index]
        else:
            up_limit = up_limit_val
        
        if isinstance(down_limit_val, list):
            down_limit = down_limit_val[hour_index]
        else:
            down_limit = down_limit_val
            
        return up_limit, down_limit

    def get_zone_net_position_delta_limits(self, zone_id, hour_index):
        """Gets net position delta limits (up_limit, down_limit) for a bidding zone for a given 1h period (0-23)."""
        if not (0 <= hour_index <= 23):
            raise ValueError("hour_index must be between 0 and 23.")
        
        zone_limits_data = self.zone_np_delta_limits.get(zone_id)
        if not zone_limits_data:
            # no limits(infinite delta)
            return float('inf'), float('inf')

        up_limit = zone_limits_data['up_profile'][hour_index]
        down_limit = zone_limits_data['down_profile'][hour_index]
        return up_limit, down_limit
