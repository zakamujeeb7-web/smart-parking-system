"""
RollbackManager Module - Handles rollback/undo functionality
"""

from typing import List, Optional
from datetime import datetime


class RollbackManager:
    """
    Manages rollback operations for parking allocations
    Uses a stack-based approach to undo last k operations
    """

    def __init__(self, max_stack_size: int = 100):
        """
        Initialize RollbackManager

        Args:
            max_stack_size: Maximum number of operations to store
        """
        self.operation_stack = []
        self.max_stack_size = max_stack_size

    def record_allocation(self, request, slot):
        """
        Record an allocation operation for potential rollback

        Args:
            request: ParkingRequest object that was allocated
            slot: ParkingSlot object that was allocated
        """
        operation = {
            'type': 'ALLOCATION',
            'request_id': request.request_id,
            'slot': slot,
            'previous_state': request.state,
            'timestamp': datetime.now(),
            'request': request  # Store reference to request object
        }

        self.operation_stack.append(operation)

        # Enforce max stack size
        if len(self.operation_stack) > self.max_stack_size:
            self.operation_stack.pop(0)  # Remove oldest operation

    def rollback_last_k(self, k: int) -> List[dict]:
        """
        Rollback the last k allocation operations

        Args:
            k: Number of operations to rollback

        Returns:
            List of rolled back operations

        Raises:
            ValueError: If k is invalid
        """
        if k <= 0:
            raise ValueError("k must be greater than 0")

        if k > len(self.operation_stack):
            raise ValueError(
                f"Cannot rollback {k} operations. Only {len(self.operation_stack)} available."
            )

        rolled_back_operations = []

        for _ in range(k):
            operation = self.operation_stack.pop()

            # Free the slot
            operation['slot'].release()

            # Restore request to previous state
            # Note: We need to restore to the state BEFORE allocation
            # If previous_state was REQUESTED, restore to REQUESTED
            request = operation['request']
            request.state = operation['previous_state']
            request.allocated_slot = None

            # Clear start_time if we're rolling back an OCCUPIED state
            if request.state.value == 'REQUESTED':
                request.start_time = None

            rolled_back_operations.append(operation)

        return rolled_back_operations

    def get_stack_size(self) -> int:
        """Get current number of operations in stack"""
        return len(self.operation_stack)

    def clear_stack(self):
        """Clear all operations from stack"""
        self.operation_stack.clear()

    def __str__(self):
        return f"RollbackManager(stack_size={len(self.operation_stack)}/{self.max_stack_size})"