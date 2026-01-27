"""
Zone Module - Represents a parking zone in the city
"""


class Zone:
    """Represents a parking zone with multiple parking areas"""

    def __init__(self, zone_id: str, zone_name: str):
        """
        Initialize a Zone

        Args:
            zone_id: Unique zone identifier
            zone_name: Human-readable zone name
        """
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.parking_areas = []
        self.adjacent_zones = []

    def add_parking_area(self, parking_area):
        """Add a parking area to this zone"""
        self.parking_areas.append(parking_area)

    def add_adjacent_zone(self, zone_id: str):
        """Register an adjacent zone"""
        if zone_id not in self.adjacent_zones:
            self.adjacent_zones.append(zone_id)

    def get_all_slots(self):
        """Get all parking slots in this zone"""
        slots = []
        for area in self.parking_areas:
            slots.extend(area.slots)
        return slots

    def get_available_slots(self):
        """Get all available parking slots"""
        return [slot for slot in self.get_all_slots() if slot.is_available]

    def __str__(self):
        return f"Zone({self.zone_id}, {self.zone_name})"
