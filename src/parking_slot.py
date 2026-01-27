"""
ParkingSlot Module - Represents an individual parking slot
"""


class ParkingSlot:
    """Represents a single parking slot"""

    def __init__(self, slot_id: str, zone_id: str):
        """
        Initialize a ParkingSlot

        Args:
            slot_id: Unique slot identifier
            zone_id: Parent zone identifier
        """
        self.slot_id = slot_id
        self.zone_id = zone_id
        self.is_available = True
        self.current_vehicle = None

    def occupy(self, vehicle):
        """Mark slot as occupied by a vehicle"""
        if not self.is_available:
            raise ValueError(f"Slot {self.slot_id} is already occupied")
        self.is_available = False
        self.current_vehicle = vehicle

    def release(self):
        """Mark slot as available"""
        self.is_available = True
        self.current_vehicle = None

    def __str__(self):
        status = "Available" if self.is_available else f"Occupied by {self.current_vehicle}"
        return f"Slot({self.slot_id}, {status})"
