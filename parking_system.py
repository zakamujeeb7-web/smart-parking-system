"""
ParkingSystem Module - Main orchestration for the smart parking system
Integrates Zone management, AllocationEngine, and RollbackManager
"""

from typing import Dict, List, Optional
from datetime import datetime
from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle
from src.parking_request import ParkingRequest, RequestState
from src.allocation_engine import AllocationEngine
from src.rollback_manager import RollbackManager


class ParkingSystem:
    """
    Main parking system that orchestrates all components
    Manages the complete lifecycle of parking requests
    """

    def __init__(self):
        """Initialize the parking system"""
        self.zones: Dict[str, Zone] = {}
        self.allocation_engine = AllocationEngine()
        self.rollback_manager = RollbackManager(max_stack_size=100)
        self.request_history: List[ParkingRequest] = []
        self.request_counter = 0

    def add_zone(self, zone: Zone):
        """
        Add a zone to the city

        Args:
            zone: Zone object to add
        """
        self.zones[zone.zone_id] = zone

    def create_parking_request(self, vehicle: Vehicle, zone_id: str) -> ParkingRequest:
        """
        Create a new parking request

        Args:
            vehicle: Vehicle requesting parking
            zone_id: Requested zone ID

        Returns:
            New ParkingRequest object
        """
        self.request_counter += 1
        request_id = f"R{self.request_counter:04d}"
        request = ParkingRequest(request_id, vehicle, zone_id)
        self.request_history.append(request)
        return request

    def process_request(self, request: ParkingRequest) -> bool:
        """
        Process a parking request and allocate a slot

        Args:
            request: ParkingRequest to process

        Returns:
            True if allocation successful, False otherwise
        """
        # Validate request is in REQUESTED state
        if request.state != RequestState.REQUESTED:
            raise ValueError(
                f"Request {request.request_id} must be in REQUESTED state. "
                f"Current state: {request.state.value}"
            )

        # Attempt allocation
        allocation_result = self.allocation_engine.allocate_parking(request, self.zones)

        if allocation_result is None:
            # No slots available
            return False

        slot, is_cross_zone = allocation_result

        # Allocate the slot
        slot.occupy(request.vehicle)

        # Update request
        request.allocated_slot = slot
        request.is_cross_zone = is_cross_zone
        request.transition_to(RequestState.ALLOCATED)

        # Record operation for rollback
        self.rollback_manager.record_allocation(request, slot)

        return True

    def occupy_parking(self, request_id: str) -> bool:
        """
        Mark an allocated parking slot as occupied (vehicle arrived)

        Args:
            request_id: Request ID to mark as occupied

        Returns:
            True if successful, False otherwise
        """
        request = self._find_request(request_id)
        if not request:
            return False

        # Must be in ALLOCATED state
        if request.state != RequestState.ALLOCATED:
            raise ValueError(
                f"Request {request_id} must be in ALLOCATED state. "
                f"Current state: {request.state.value}"
            )

        # Transition to OCCUPIED
        request.transition_to(RequestState.OCCUPIED)
        return True

    def release_parking(self, request_id: str) -> bool:
        """
        Release a parking slot (vehicle leaving)

        Args:
            request_id: Request ID to release

        Returns:
            True if successful, False otherwise
        """
        request = self._find_request(request_id)
        if not request:
            return False

        # Must be in OCCUPIED state
        if request.state != RequestState.OCCUPIED:
            raise ValueError(
                f"Request {request_id} must be in OCCUPIED state to release. "
                f"Current state: {request.state.value}"
            )

        # Release the slot
        if request.allocated_slot:
            request.allocated_slot.release()

        # Transition to RELEASED
        request.transition_to(RequestState.RELEASED)
        return True

    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a parking request

        Args:
            request_id: Request ID to cancel

        Returns:
            True if successful, False otherwise
        """
        request = self._find_request(request_id)
        if not request:
            return False

        # Can only cancel from REQUESTED or ALLOCATED states
        if request.state not in [RequestState.REQUESTED, RequestState.ALLOCATED]:
            raise ValueError(
                f"Cannot cancel request {request_id} in {request.state.value} state. "
                f"Can only cancel from REQUESTED or ALLOCATED states."
            )

        # If slot was allocated, release it
        if request.state == RequestState.ALLOCATED and request.allocated_slot:
            request.allocated_slot.release()

        # Transition to CANCELLED
        request.transition_to(RequestState.CANCELLED)
        return True

    def rollback_last_allocations(self, k: int) -> List[str]:
        """
        Rollback the last k allocations

        Args:
            k: Number of allocations to rollback

        Returns:
            List of request IDs that were rolled back
        """
        rolled_back_ops = self.rollback_manager.rollback_last_k(k)
        return [op['request_id'] for op in rolled_back_ops]

    def get_zone_status(self, zone_id: str) -> Optional[Dict]:
        """
        Get status information for a zone

        Args:
            zone_id: Zone ID to query

        Returns:
            Dictionary with zone statistics or None if zone not found
        """
        if zone_id not in self.zones:
            return None

        zone = self.zones[zone_id]
        all_slots = zone.get_all_slots()
        available_slots = zone.get_available_slots()

        return {
            'zone_id': zone_id,
            'zone_name': zone.zone_name,
            'total_slots': len(all_slots),
            'available_slots': len(available_slots),
            'occupied_slots': len(all_slots) - len(available_slots),
            'utilization_rate': (
                (len(all_slots) - len(available_slots)) / len(all_slots) * 100
                if all_slots else 0
            )
        }

    def get_all_requests(self) -> List[ParkingRequest]:
        """Get all parking requests"""
        return self.request_history

    def get_requests_by_state(self, state: RequestState) -> List[ParkingRequest]:
        """
        Get all requests in a specific state

        Args:
            state: RequestState to filter by

        Returns:
            List of requests in the specified state
        """
        return [req for req in self.request_history if req.state == state]

    def _find_request(self, request_id: str) -> Optional[ParkingRequest]:
        """
        Find a request by ID

        Args:
            request_id: Request ID to find

        Returns:
            ParkingRequest object or None
        """
        for request in self.request_history:
            if request.request_id == request_id:
                return request
        return None

    def get_system_summary(self) -> Dict:
        """
        Get overall system statistics

        Returns:
            Dictionary with system-wide statistics
        """
        total_slots = sum(len(zone.get_all_slots()) for zone in self.zones.values())
        total_available = sum(
            len(zone.get_available_slots()) for zone in self.zones.values()
        )

        return {
            'total_zones': len(self.zones),
            'total_slots': total_slots,
            'available_slots': total_available,
            'occupied_slots': total_slots - total_available,
            'total_requests': len(self.request_history),
            'requested': len(self.get_requests_by_state(RequestState.REQUESTED)),
            'allocated': len(self.get_requests_by_state(RequestState.ALLOCATED)),
            'occupied': len(self.get_requests_by_state(RequestState.OCCUPIED)),
            'released': len(self.get_requests_by_state(RequestState.RELEASED)),
            'cancelled': len(self.get_requests_by_state(RequestState.CANCELLED)),
            'rollback_stack_size': self.rollback_manager.get_stack_size()
        }

    def __str__(self):
        summary = self.get_system_summary()
        return (
            f"ParkingSystem({summary['total_zones']} zones, "
            f"{summary['total_slots']} slots, "
            f"{summary['total_requests']} requests)"
        )