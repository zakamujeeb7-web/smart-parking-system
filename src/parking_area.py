"""
ParkingArea Module - Represents a parking area within a zone
"""


class ParkingArea:
    """Represents a parking area containing multiple slots"""

    def __init__(self, area_id: str, zone_id: str):
        """
        Initialize a ParkingArea

        Args:
            area_id: Unique area identifier
            zone_id: Parent zone identifier
        """
        self.area_id = area_id
        self.zone_id = zone_id
        self.slots = []

    def add_slot(self, slot):
        """Add a parking slot to this area"""
        self.slots.append(slot)

    def get_available_slots(self):
        """Get all available slots in this area"""
        return [slot for slot in self.slots if slot.is_available]

    def __str__(self):
        return f"ParkingArea({self.area_id}, Zone: {self.zone_id})"
