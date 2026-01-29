"""
Test Phase 3 - Allocation Engine
"""

from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle
from src.parking_request import ParkingRequest
from src.allocation_engine import AllocationEngine


def test_phase_3():
    """Test allocation engine functionality"""

    print("🧪 Testing Phase 3: Allocation Engine\n")

    # Setup test city
    engine = AllocationEngine()

    # Create Zone A with 2 slots
    zone_a = Zone("ZA", "Zone A")
    area_a1 = ParkingArea("AA1", "ZA")
    slot_a1 = ParkingSlot("SA1", "ZA")
    slot_a2 = ParkingSlot("SA2", "ZA")
    area_a1.add_slot(slot_a1)
    area_a1.add_slot(slot_a2)
    zone_a.add_parking_area(area_a1)

    # Create Zone B with 1 slot (adjacent to A)
    zone_b = Zone("ZB", "Zone B")
    area_b1 = ParkingArea("AB1", "ZB")
    slot_b1 = ParkingSlot("SB1", "ZB")
    area_b1.add_slot(slot_b1)
    zone_b.add_parking_area(area_b1)

    # Set adjacency
    zone_a.add_adjacent_zone("ZB")

    zones = {"ZA": zone_a, "ZB": zone_b}

    # Test 1: Same-zone allocation
    print("Test 1: Allocate in requested zone")
    vehicle1 = Vehicle("V001", "ZA")
    request1 = ParkingRequest("R001", vehicle1, "ZA")
    result = engine.allocate_parking(request1, zones)

    if result and result[0].slot_id == "SA1" and result[1] == False:
        print("✅ PASS: Allocated SA1 in Zone A (same zone, no penalty)\n")
    else:
        print("❌ FAIL: Same-zone allocation failed\n")
        return False

    # Occupy the slot
    slot_a1.occupy(vehicle1)

    # Test 2: Same-zone allocation (second slot)
    print("Test 2: Allocate second slot in same zone")
    vehicle2 = Vehicle("V002", "ZA")
    request2 = ParkingRequest("R002", vehicle2, "ZA")
    result = engine.allocate_parking(request2, zones)

    if result and result[0].slot_id == "SA2" and result[1] == False:
        print("✅ PASS: Allocated SA2 in Zone A (same zone, no penalty)\n")
    else:
        print("❌ FAIL: Second same-zone allocation failed\n")
        return False

    # Occupy the second slot
    slot_a2.occupy(vehicle2)

    # Test 3: Cross-zone allocation (Zone A is full)
    print("Test 3: Cross-zone allocation (Zone A full)")
    vehicle3 = Vehicle("V003", "ZA")
    request3 = ParkingRequest("R003", vehicle3, "ZA")
    result = engine.allocate_parking(request3, zones)

    if result and result[0].slot_id == "SB1" and result[1] == True:
        print("✅ PASS: Allocated SB1 in Zone B (cross-zone, penalty applied)\n")
    else:
        print("❌ FAIL: Cross-zone allocation failed\n")
        return False

    # Occupy the cross-zone slot
    slot_b1.occupy(vehicle3)

    # Test 4: No slots available
    print("Test 4: No slots available anywhere")
    vehicle4 = Vehicle("V004", "ZA")
    request4 = ParkingRequest("R004", vehicle4, "ZA")
    result = engine.allocate_parking(request4, zones)

    if result is None:
        print("✅ PASS: Correctly returned None (no slots available)\n")
    else:
        print("❌ FAIL: Should return None when all slots occupied\n")
        return False

    # Test 5: Invalid zone
    print("Test 5: Request for non-existent zone")
    vehicle5 = Vehicle("V005", "ZX")
    request5 = ParkingRequest("R005", vehicle5, "ZX")
    result = engine.allocate_parking(request5, zones)

    if result is None:
        print("✅ PASS: Correctly returned None (invalid zone)\n")
    else:
        print("❌ FAIL: Should return None for invalid zone\n")
        return False

    print("=" * 50)
    print("✅ ALL PHASE 3 TESTS PASSED")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_phase_3()
    exit(0 if success else 1)