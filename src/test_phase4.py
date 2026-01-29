"""
Test Phase 4 - Rollback Manager
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle
from src.parking_request import ParkingRequest, RequestState
from src.allocation_engine import AllocationEngine
from src.rollback_manager import RollbackManager


def test_phase_4():
    """Test rollback manager functionality"""

    print("🧪 Testing Phase 4: Rollback Manager\n")

    # Setup
    rollback_mgr = RollbackManager(max_stack_size=10)

    # Create test zone with slots
    zone_a = Zone("ZA", "Zone A")
    area_a1 = ParkingArea("AA1", "ZA")
    slot_a1 = ParkingSlot("SA1", "ZA")
    slot_a2 = ParkingSlot("SA2", "ZA")
    slot_a3 = ParkingSlot("SA3", "ZA")
    area_a1.add_slot(slot_a1)
    area_a1.add_slot(slot_a2)
    area_a1.add_slot(slot_a3)
    zone_a.add_parking_area(area_a1)

    # Test 1: Record allocation
    print("Test 1: Record allocation operation")
    vehicle1 = Vehicle("V001", "ZA")
    request1 = ParkingRequest("R001", vehicle1, "ZA")
    request1.transition_to(RequestState.ALLOCATED)
    slot_a1.occupy(vehicle1)
    request1.allocated_slot = slot_a1

    rollback_mgr.record_allocation(request1, slot_a1)

    if rollback_mgr.get_stack_size() == 1:
        print("✅ PASS: Allocation recorded in stack\n")
    else:
        print("❌ FAIL: Allocation not recorded\n")
        return False

    # Test 2: Record multiple allocations
    print("Test 2: Record multiple allocations")
    vehicle2 = Vehicle("V002", "ZA")
    request2 = ParkingRequest("R002", vehicle2, "ZA")
    request2.transition_to(RequestState.ALLOCATED)
    slot_a2.occupy(vehicle2)
    request2.allocated_slot = slot_a2
    rollback_mgr.record_allocation(request2, slot_a2)

    vehicle3 = Vehicle("V003", "ZA")
    request3 = ParkingRequest("R003", vehicle3, "ZA")
    request3.transition_to(RequestState.ALLOCATED)
    slot_a3.occupy(vehicle3)
    request3.allocated_slot = slot_a3
    rollback_mgr.record_allocation(request3, slot_a3)

    if rollback_mgr.get_stack_size() == 3:
        print("✅ PASS: 3 allocations recorded\n")
    else:
        print(f"❌ FAIL: Expected 3, got {rollback_mgr.get_stack_size()}\n")
        return False

    # Test 3: Rollback last 2 allocations
    print("Test 3: Rollback last 2 allocations")

    # Verify slots are occupied before rollback
    if not slot_a2.is_available and not slot_a3.is_available:
        print("   Pre-rollback: SA2 and SA3 occupied ✓")
    else:
        print("❌ FAIL: Slots should be occupied before rollback\n")
        return False

    rolled_back = rollback_mgr.rollback_last_k(2)

    # Verify slots are now available
    if slot_a2.is_available and slot_a3.is_available:
        print("   Post-rollback: SA2 and SA3 available ✓")
    else:
        print("❌ FAIL: Slots should be available after rollback\n")
        return False

    # Verify request states restored
    if request2.state == RequestState.ALLOCATED and request3.state == RequestState.ALLOCATED:
        print("   Request states restored ✓")
    else:
        print(f"❌ FAIL: States not restored: R2={request2.state}, R3={request3.state}\n")
        return False

    # Verify stack size decreased
    if rollback_mgr.get_stack_size() == 1:
        print("   Stack size: 1 (correct) ✓")
        print("✅ PASS: Rollback successful\n")
    else:
        print(f"❌ FAIL: Stack size should be 1, got {rollback_mgr.get_stack_size()}\n")
        return False

    # Test 4: Rollback with k too large
    print("Test 4: Handle k larger than stack size")
    try:
        rollback_mgr.rollback_last_k(10)  # Only 1 operation in stack
        print("❌ FAIL: Should raise ValueError\n")
        return False
    except ValueError as e:
        if "Cannot rollback" in str(e):
            print(f"✅ PASS: Correctly raised ValueError: {e}\n")
        else:
            print("❌ FAIL: Wrong error message\n")
            return False

    # Test 5: Rollback with k <= 0
    print("Test 5: Handle invalid k (k <= 0)")
    try:
        rollback_mgr.rollback_last_k(0)
        print("❌ FAIL: Should raise ValueError for k=0\n")
        return False
    except ValueError as e:
        if "must be greater than 0" in str(e):
            print(f"✅ PASS: Correctly raised ValueError: {e}\n")
        else:
            print("❌ FAIL: Wrong error message\n")
            return False

    # Test 6: Max stack size enforcement
    print("Test 6: Max stack size enforcement")
    rollback_mgr_small = RollbackManager(max_stack_size=3)

    # Add 5 allocations (should keep only last 3)
    for i in range(5):
        v = Vehicle(f"V{i}", "ZA")
        r = ParkingRequest(f"R{i}", v, "ZA")
        s = ParkingSlot(f"S{i}", "ZA")
        rollback_mgr_small.record_allocation(r, s)

    if rollback_mgr_small.get_stack_size() == 3:
        print("✅ PASS: Stack size limited to max_stack_size (3)\n")
    else:
        print(f"❌ FAIL: Expected 3, got {rollback_mgr_small.get_stack_size()}\n")
        return False

    # Test 7: Rollback restores allocated_slot to None
    print("Test 7: Verify allocated_slot is cleared on rollback")
    rollback_mgr2 = RollbackManager()

    slot_test = ParkingSlot("ST1", "ZA")
    vehicle_test = Vehicle("VT1", "ZA")
    request_test = ParkingRequest("RT1", vehicle_test, "ZA")
    request_test.transition_to(RequestState.ALLOCATED)
    slot_test.occupy(vehicle_test)
    request_test.allocated_slot = slot_test

    rollback_mgr2.record_allocation(request_test, slot_test)
    rollback_mgr2.rollback_last_k(1)

    if request_test.allocated_slot is None:
        print("✅ PASS: allocated_slot cleared on rollback\n")
    else:
        print("❌ FAIL: allocated_slot should be None after rollback\n")
        return False

    # Test 8: Clear stack
    print("Test 8: Clear stack")
    rollback_mgr2.clear_stack()
    if rollback_mgr2.get_stack_size() == 0:
        print("✅ PASS: Stack cleared successfully\n")
    else:
        print("❌ FAIL: Stack not cleared\n")
        return False

    print("=" * 50)
    print("✅ ALL PHASE 4 TESTS PASSED")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_phase_4()
    sys.exit(0 if success else 1)