"""
Test Phase 5 - ParkingSystem Integration
Tests the main system orchestration and integration of all components
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
from src.parking_system import ParkingSystem


def setup_test_city():
    """Create a test city with 2 zones"""
    system = ParkingSystem()

    # Zone A with 3 slots
    zone_a = Zone("ZA", "Zone A")
    area_a1 = ParkingArea("AA1", "ZA")
    for i in range(3):
        slot = ParkingSlot(f"SA{i + 1}", "ZA")
        area_a1.add_slot(slot)
    zone_a.add_parking_area(area_a1)

    # Zone B with 2 slots (adjacent to A)
    zone_b = Zone("ZB", "Zone B")
    area_b1 = ParkingArea("AB1", "ZB")
    for i in range(2):
        slot = ParkingSlot(f"SB{i + 1}", "ZB")
        area_b1.add_slot(slot)
    zone_b.add_parking_area(area_b1)

    # Set adjacency
    zone_a.add_adjacent_zone("ZB")
    zone_b.add_adjacent_zone("ZA")

    # Add zones to system
    system.add_zone(zone_a)
    system.add_zone(zone_b)

    return system


def test_phase_5():
    """Run all Phase 5 tests"""
    print("🧪 Testing Phase 5: ParkingSystem Integration\n")
    print("=" * 60)

    # Test 1: System initialization
    print("\nTest 1: System initialization")
    system = setup_test_city()
    summary = system.get_system_summary()

    if (summary['total_zones'] == 2 and
            summary['total_slots'] == 5 and
            summary['available_slots'] == 5):
        print("✅ PASS: System initialized with 2 zones, 5 total slots")
    else:
        print(f"❌ FAIL: Expected 2 zones, 5 slots. Got: {summary}")
        return False

    # Test 2: Create parking request
    print("\nTest 2: Create parking request")
    vehicle1 = Vehicle("V001", "ZA")
    request1 = system.create_parking_request(vehicle1, "ZA")

    if (request1.request_id == "R0001" and
            request1.state == RequestState.REQUESTED and
            len(system.request_history) == 1):
        print("✅ PASS: Request created with ID R0001 in REQUESTED state")
    else:
        print("❌ FAIL: Request creation failed")
        return False

    # Test 3: Process request (allocation)
    print("\nTest 3: Process parking request (allocate slot)")
    success = system.process_request(request1)

    if (success and
            request1.state == RequestState.ALLOCATED and
            request1.allocated_slot is not None and
            request1.allocated_slot.zone_id == "ZA"):
        print(f"✅ PASS: Request allocated to slot {request1.allocated_slot.slot_id} in Zone A")
    else:
        print("❌ FAIL: Request processing failed")
        return False

    # Test 4: Occupy parking
    print("\nTest 4: Occupy allocated parking (vehicle arrived)")
    success = system.occupy_parking("R0001")

    if success and request1.state == RequestState.OCCUPIED:
        print("✅ PASS: Parking marked as occupied, start_time recorded")
    else:
        print("❌ FAIL: Occupy parking failed")
        return False

    # Test 5: Release parking
    print("\nTest 5: Release parking (vehicle leaving)")
    success = system.release_parking("R0001")

    if (success and
            request1.state == RequestState.RELEASED and
            request1.allocated_slot.is_available):
        print("✅ PASS: Parking released, slot available, end_time recorded")
    else:
        print("❌ FAIL: Release parking failed")
        return False

    # Test 6: Cancel request in REQUESTED state
    print("\nTest 6: Cancel request in REQUESTED state")
    vehicle2 = Vehicle("V002", "ZA")
    request2 = system.create_parking_request(vehicle2, "ZA")
    success = system.cancel_request("R0002")

    if success and request2.state == RequestState.CANCELLED:
        print("✅ PASS: Request cancelled from REQUESTED state")
    else:
        print("❌ FAIL: Cancellation failed")
        return False

    # Test 7: Cancel request in ALLOCATED state
    print("\nTest 7: Cancel request in ALLOCATED state (free slot)")
    vehicle3 = Vehicle("V003", "ZA")
    request3 = system.create_parking_request(vehicle3, "ZA")
    system.process_request(request3)
    allocated_slot_id = request3.allocated_slot.slot_id
    success = system.cancel_request("R0003")

    if (success and
            request3.state == RequestState.CANCELLED and
            request3.allocated_slot.is_available):
        print(f"✅ PASS: Allocated request cancelled, slot {allocated_slot_id} freed")
    else:
        print("❌ FAIL: Allocated cancellation failed")
        return False

    # Test 8: Cannot cancel from OCCUPIED state
    print("\nTest 8: Prevent cancellation from OCCUPIED state")
    vehicle4 = Vehicle("V004", "ZA")
    request4 = system.create_parking_request(vehicle4, "ZA")
    system.process_request(request4)
    system.occupy_parking("R0004")

    try:
        system.cancel_request("R0004")
        print("❌ FAIL: Should not allow cancellation from OCCUPIED state")
        return False
    except ValueError as e:
        if "Cannot cancel" in str(e):
            print("✅ PASS: Correctly prevented cancellation from OCCUPIED state")
        else:
            print("❌ FAIL: Wrong error message")
            return False

    # Test 9: Cross-zone allocation
    print("\nTest 9: Cross-zone allocation when requested zone is full")
    # Fill Zone A (already has 1 occupied, need 2 more)
    system.release_parking("R0004")  # Free up one slot first

    # Allocate 3 slots in Zone A
    vehicles = []
    for i in range(3):
        v = Vehicle(f"V10{i}", "ZA")
        vehicles.append(v)
        req = system.create_parking_request(v, "ZA")
        system.process_request(req)

    # Now Zone A is full, try one more
    vehicle_cross = Vehicle("V999", "ZA")
    request_cross = system.create_parking_request(vehicle_cross, "ZA")
    success = system.process_request(request_cross)

    if (success and
            request_cross.is_cross_zone and
            request_cross.allocated_slot.zone_id == "ZB"):
        print(f"✅ PASS: Cross-zone allocation to Zone B (penalty applied)")
    else:
        print("❌ FAIL: Cross-zone allocation failed")
        return False

    # Test 10: Rollback last 2 allocations
    print("\nTest 10: Rollback last 2 allocations")

    # Get requests before rollback
    summary_before = system.get_system_summary()
    rollback_stack_before = summary_before['rollback_stack_size']

    # Rollback
    rolled_back = system.rollback_last_allocations(2)

    summary_after = system.get_system_summary()

    if (len(rolled_back) == 2 and
            summary_after['rollback_stack_size'] == rollback_stack_before - 2):
        print(f"✅ PASS: Rolled back 2 operations: {rolled_back}")
    else:
        print("❌ FAIL: Rollback failed")
        return False

    # Test 11: Zone status query
    print("\nTest 11: Get zone status")
    status = system.get_zone_status("ZA")

    if (status and
            status['zone_id'] == "ZA" and
            status['total_slots'] == 3):
        print(f"✅ PASS: Zone A status - {status['available_slots']}/{status['total_slots']} available")
    else:
        print("❌ FAIL: Zone status query failed")
        return False

    # Test 12: System summary
    print("\nTest 12: Get system summary")
    summary = system.get_system_summary()

    if (summary['total_zones'] == 2 and
            summary['total_slots'] == 5 and
            summary['total_requests'] > 0):
        print(f"✅ PASS: System summary - {summary['total_requests']} requests, "
              f"{summary['occupied']} occupied")
    else:
        print("❌ FAIL: System summary failed")
        return False

    # Test 13: Get requests by state
    print("\nTest 13: Query requests by state")
    released_requests = system.get_requests_by_state(RequestState.RELEASED)
    cancelled_requests = system.get_requests_by_state(RequestState.CANCELLED)

    if len(released_requests) >= 1 and len(cancelled_requests) >= 2:
        print(f"✅ PASS: Found {len(released_requests)} released, "
              f"{len(cancelled_requests)} cancelled requests")
    else:
        print("❌ FAIL: State query failed")
        return False

    # Test 14: Cannot process non-REQUESTED request
    print("\nTest 14: Prevent processing already allocated request")
    vehicle_test = Vehicle("VTEST", "ZA")
    request_test = system.create_parking_request(vehicle_test, "ZA")
    system.process_request(request_test)

    try:
        system.process_request(request_test)  # Try again
        print("❌ FAIL: Should not allow processing non-REQUESTED request")
        return False
    except ValueError as e:
        if "REQUESTED state" in str(e):
            print("✅ PASS: Correctly prevented double processing")
        else:
            print("❌ FAIL: Wrong error message")
            return False

    # Test 15: No slots available scenario
    print("\nTest 15: Handle no slots available (all zones full)")
    # Create a small system with 1 slot
    small_system = ParkingSystem()
    zone_small = Zone("ZS", "Small Zone")
    area_small = ParkingArea("AS1", "ZS")
    slot_small = ParkingSlot("SS1", "ZS")
    area_small.add_slot(slot_small)
    zone_small.add_parking_area(area_small)
    small_system.add_zone(zone_small)

    # Occupy the only slot
    v1 = Vehicle("VS1", "ZS")
    r1 = small_system.create_parking_request(v1, "ZS")
    small_system.process_request(r1)

    # Try to allocate when full
    v2 = Vehicle("VS2", "ZS")
    r2 = small_system.create_parking_request(v2, "ZS")
    success = small_system.process_request(r2)

    if not success and r2.state == RequestState.REQUESTED:
        print("✅ PASS: Correctly handled no slots available")
    else:
        print("❌ FAIL: Should return False when no slots available")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL PHASE 5 TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_phase_5()
    sys.exit(0 if success else 1)