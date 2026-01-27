"""
ParkingRequest Module - Manages parking request lifecycle
"""

from enum import Enum
from datetime import datetime


class RequestState(Enum):
    """Possible states for a parking request"""
    REQUESTED = "REQUESTED"
    ALLOCATED = "ALLOCATED"
    OCCUPIED = "OCCUPIED"
    RELEASED = "RELEASED"
    CANCELLED = "CANCELLED"


class ParkingRequest:
    """Represents a parking request with state machine"""

    # Valid state transitions
    VALID_TRANSITIONS = {
        RequestState.REQUESTED: [RequestState.ALLOCATED, RequestState.CANCELLED],
        RequestState.ALLOCATED: [RequestState.OCCUPIED, RequestState.CANCELLED],
        RequestState.OCCUPIED: [RequestState.RELEASED],
        RequestState.RELEASED: [],
        RequestState.CANCELLED: []
    }

    def __init__(self, request_id: str, vehicle, requested_zone: str):
        """
        Initialize a ParkingRequest

        Args:
            request_id: Unique request identifier
            vehicle: Vehicle object making the request
            requested_zone: Requested zone ID
        """
        self.request_id = request_id
        self.vehicle = vehicle
        self.requested_zone = requested_zone
        self.request_time = datetime.now()
        self.state = RequestState.REQUESTED
        self.allocated_slot = None
        self.start_time = None
        self.end_time = None
        self.is_cross_zone = False

    def transition_to(self, new_state: RequestState):
        """
        Transition to a new state

        Args:
            new_state: Target state

        Raises:
            ValueError: If transition is invalid
        """
        if new_state not in self.VALID_TRANSITIONS[self.state]:
            raise ValueError(
                f"Invalid transition from {self.state.value} to {new_state.value}"
            )
        self.state = new_state

        # Update timestamps
        if new_state == RequestState.OCCUPIED:
            self.start_time = datetime.now()
        elif new_state == RequestState.RELEASED:
            self.end_time = datetime.now()

    def __str__(self):
        return f"Request({self.request_id}, {self.state.value})"
