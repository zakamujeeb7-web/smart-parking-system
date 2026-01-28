"""
AllocationEngine Module - Handles parking slot allocation logic
"""

from typing import Optional, Tuple, List
from src.parking_slot import ParkingSlot


class AllocationEngine:
    """
    Allocation engine for parking slot assignment
    Implements same-zone preference and cross-zone fallback
    """

    def allocate_parking(self, request, zones: dict) -> Optional[Tuple[ParkingSlot, bool]]:
        """
        Allocate a parking slot for a request

        Args:
            request: ParkingRequest object
            zones: Dictionary of {zone_id: Zone object}

        Returns:
            Tuple of (ParkingSlot, is_cross_zone) if successful
            None if no slots available
        """
        requested_zone_id = request.requested_zone

        # Validate zone exists
        if requested_zone_id not in zones:
            return None

        # Strategy 1: Try same zone first
        slot = self._find_slot_in_zone(zones[requested_zone_id])
        if slot:
            return (slot, False)  # Found in same zone, no penalty

        # Strategy 2: Try adjacent zones
        slot = self._find_slot_in_adjacent_zones(
            zones[requested_zone_id], 
            zones
        )
        if slot:
            return (slot, True)  # Found in adjacent zone, apply penalty

        # No slots available anywhere
        return None

    def _find_slot_in_zone(self, zone) -> Optional[ParkingSlot]:
        """
        Find first available slot in a zone

        Args:
            zone: Zone object to search

        Returns:
            First available ParkingSlot or None
        """
        available_slots = zone.get_available_slots()
        return available_slots[0] if available_slots else None

    def _find_slot_in_adjacent_zones(self, origin_zone, all_zones: dict) -> Optional[ParkingSlot]:
        """
        Search adjacent zones for available slot

        Args:
            origin_zone: The originally requested Zone
            all_zones: Dictionary of all zones {zone_id: Zone}

        Returns:
            First available ParkingSlot from adjacent zones or None
        """
        for adjacent_zone_id in origin_zone.adjacent_zones:
            if adjacent_zone_id in all_zones:
                adjacent_zone = all_zones[adjacent_zone_id]
                slot = self._find_slot_in_zone(adjacent_zone)
                if slot:
                    return slot

        return None