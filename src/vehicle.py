"""
Vehicle Module - Represents a vehicle requesting parking
"""


class Vehicle:
    """Represents a vehicle in the parking system"""

    def __init__(self, vehicle_id: str, preferred_zone: str):
        """
        Initialize a Vehicle

        Args:
            vehicle_id: Unique vehicle identifier
            preferred_zone: Preferred parking zone ID
        """
        self.vehicle_id = vehicle_id
        self.preferred_zone = preferred_zone

    def __str__(self):
        return f"Vehicle({self.vehicle_id}, prefers {self.preferred_zone})"
