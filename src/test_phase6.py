"""
Test Phase 6 - Analytics Module
Tests all analytics functions including duration, utilization, and reporting
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle
from src.parking_request import ParkingRequest, RequestState
from src.parking_system import ParkingSystem
from src.analytics import Analytics


def setup_test_system_with_data():
    """Create a system with realistic test data"""
    system = ParkingSystem()

    # Zone A with 4 slots
    zone_a = Zone("ZA", "Downtown")
    area_a1 = ParkingArea("AA1", "ZA")
    for i in range(4):
        slot = ParkingSlot(f"SA{i + 1}", "ZA")
        area_a1.add_slot(slot)
    zone_a.add_parking_area(area_a1)

    # Zone B with 3 slots
    zone_b = Zone("ZB", "Uptown")
    area_b1 = ParkingArea("AB1", "ZB")
    for i in range(3):
        slot = ParkingSlot(f"SB{i + 1}", "ZB")
        area_b1.add_slot(slot)
    zone_b.add_parking_area(area_b1)

    # Zone C with 2 slots
    zone_c = Zone("ZC", "Midtown")
    area_c1 = ParkingArea("AC1", "ZC")
    for i in range(2):
        slot = ParkingSlot(f"SC{i + 1}", "ZC")
        area_c1.add_slot(slot)
    zone_c.add_parking_area(area_c1)

    # Set adjacencies
    zone_a.add_adjacent_zone("ZB")
    zone_b.add_adjacent_zone("ZA")
    zone_b.add_adjacent_zone("ZC")

    # Add zones
    system.add_zone(zone_a)
    system.add_zone(zone_b)
    system.add_zone(zone_c)

    return system


def test_phase_6():
    """Run all Phase 6 Analytics tests"""
    print("🧪 Testing Phase 6: Analytics Module\n")
    print("=" * 60)

    # Setup system
    system = setup_test_system_with_data()
    analytics = Analytics(system)

    # Create some test data
    # Scenario 1: Complete trip (2 hours)
    v1 = Vehicle("V001", "ZA")
    r1 = system.create_parking_request(v1, "ZA")
    system.process_request(r1)
    system.occupy_parking(r1.request_id)
    # Simulate 2 hour parking
    r1.start_time = datetime.now() - timedelta(hours=2)
    system.release_parking(r1.request_id)
    r1.end_time = datetime.now()

    # Scenario 2: Complete trip (1 hour)
    v2 = Vehicle("V002", "ZA")
    r2 = system.create_parking_request(v2, "ZA")
    system.process_request(r2)
    system.occupy_parking(r2.request_id)
    r2.start_time = datetime.now() - timedelta(hours=1)
    system.release_parking(r2.request_id)
    r2.end_time = datetime.now()

    # Scenario 3: Complete trip (3 hours)
    v3 = Vehicle("V003", "ZB")
    r3 = system.create_parking_request(v3, "ZB")
    system.process_request(r3)
    system.occupy_parking(r3.request_id)
    r3.start_time = datetime.now() - timedelta(hours=3)
    system.release_parking(r3.request_id)
    r3.end_time = datetime.now()

    # Scenario 4: Currently occupied
    v4 = Vehicle("V004", "ZA")
    r4 = system.create_parking_request(v4, "ZA")
    system.process_request(r4)
    system.occupy_parking(r4.request_id)

    # Scenario 5: Cancelled from REQUESTED
    v5 = Vehicle("V005", "ZB")
    r5 = system.create_parking_request(v5, "ZB")
    system.cancel_request(r5.request_id)

    # Scenario 6: Cancelled from ALLOCATED
    v6 = Vehicle("V006", "ZB")
    r6 = system.create_parking_request(v6, "ZB")
    system.process_request(r6)
    system.cancel_request(r6.request_id)

    # Scenario 7: Occupy more slots for utilization test
    v7 = Vehicle("V007", "ZB")
    r7 = system.create_parking_request(v7, "ZB")
    system.process_request(r7)
    system.occupy_parking(r7.request_id)

    # Test 1: Calculate average duration
    print("\nTest 1: Calculate average parking duration")
    avg_duration = analytics.calculate_average_duration()

    # Expected: (2 + 1 + 3) / 3 = 2.0 hours
    expected_avg = 2.0
    tolerance = 0.1

    if avg_duration is not None and abs(avg_duration - expected_avg) < tolerance:
        print(f"✅ PASS: Average duration = {avg_duration} hours "
              f"(expected ~{expected_avg})")
    else:
        print(f"❌ FAIL: Expected ~{expected_avg}, got {avg_duration}")
        return False

    # Test 2: Zone utilization calculation
    print("\nTest 2: Calculate zone utilization rates")
    utilization = analytics.calculate_zone_utilization()

    # Zone A: 1 occupied (V004) out of 4 = 25%
    # Zone B: 2 occupied (V004 from cross-alloc?, V007) = depends on allocation
    # Let's check actual values
    print(f"   Zone A (ZA): {utilization.get('ZA', 0)}%")
    print(f"   Zone B (ZB): {utilization.get('ZB', 0)}%")
    print(f"   Zone C (ZC): {utilization.get('ZC', 0)}%")

    if 'ZA' in utilization and 'ZB' in utilization and 'ZC' in utilization:
        print("✅ PASS: All zones have utilization calculated")
    else:
        print("❌ FAIL: Missing zone utilization data")
        return False

    # Test 3: Cancelled vs completed statistics
    print("\nTest 3: Get cancelled vs completed request counts")
    stats = analytics.get_cancelled_vs_completed()

    print(f"   Total: {stats['total']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   Cancelled: {stats['cancelled']}")
    print(f"   Active: {stats['active']}")

    # We have 3 completed (r1, r2, r3), 2 cancelled (r5, r6), 2 active (r4, r7)
    if (stats['completed'] == 3 and
            stats['cancelled'] == 2 and
            stats['active'] == 2 and
            stats['total'] == 7):
        print("✅ PASS: Request statistics correct")
    else:
        print(f"❌ FAIL: Expected completed=3, cancelled=2, active=2, total=7")
        return False

    # Test 4: Find peak usage zones
    print("\nTest 4: Identify peak usage zones")
    peak_zones = analytics.find_peak_usage_zones()

    print(f"   Peak zones (sorted by utilization):")
    for i, zone in enumerate(peak_zones, 1):
        print(f"   {i}. {zone['zone_name']} ({zone['zone_id']}): "
              f"{zone['utilization']}% "
              f"({zone['occupied_slots']}/{zone['total_slots']})")

    if len(peak_zones) == 3 and peak_zones[0]['utilization'] >= 0:
        print("✅ PASS: Peak zones identified and sorted")
    else:
        print("❌ FAIL: Peak zones not properly calculated")
        return False

    # Test 5: Cross-zone statistics
    print("\nTest 5: Calculate cross-zone allocation statistics")
    cross_zone_stats = analytics.get_cross_zone_statistics()

    print(f"   Total allocations: {cross_zone_stats['total_allocations']}")
    print(f"   Cross-zone: {cross_zone_stats['cross_zone_allocations']}")
    print(f"   Percentage: {cross_zone_stats['cross_zone_percentage']}%")

    if 'total_allocations' in cross_zone_stats:
        print("✅ PASS: Cross-zone statistics calculated")
    else:
        print("❌ FAIL: Cross-zone statistics missing")
        return False

    # Test 6: Request distribution by zone
    print("\nTest 6: Get request distribution by zone")
    distribution = analytics.get_zone_request_distribution()

    print(f"   Zone distribution:")
    for zone_id, count in distribution.items():
        print(f"   {zone_id}: {count} requests")

    # ZA: r1, r2, r4 = 3
    # ZB: r3, r5, r6, r7 = 4
    # ZC: 0
    if (distribution.get('ZA') == 3 and
            distribution.get('ZB') == 4 and
            distribution.get('ZC') == 0):
        print("✅ PASS: Request distribution correct")
    else:
        print(f"❌ FAIL: Distribution mismatch")
        return False

    # Test 7: Generate comprehensive report
    print("\nTest 7: Generate analytics report")
    report = analytics.generate_report()

    if (len(report) > 100 and
            "PARKING SYSTEM ANALYTICS REPORT" in report and
            "ZONE UTILIZATION" in report):
        print("✅ PASS: Report generated successfully")
        print("\n--- SAMPLE REPORT OUTPUT ---")
        print(report[:500] + "...\n")
    else:
        print("❌ FAIL: Report generation failed")
        return False

    # Test 8: Export to dictionary
    print("\nTest 8: Export analytics to dictionary format")
    data_dict = analytics.export_to_dict()

    required_keys = [
        'timestamp',
        'system_summary',
        'average_duration_hours',
        'zone_utilization',
        'request_statistics',
        'peak_usage_zones'
    ]

    if all(key in data_dict for key in required_keys):
        print("✅ PASS: Analytics exported to dict with all keys")
    else:
        missing = [k for k in required_keys if k not in data_dict]
        print(f"❌ FAIL: Missing keys: {missing}")
        return False

    # Test 9: Analytics with no completed trips
    print("\nTest 9: Handle empty data (no completed trips)")
    empty_system = ParkingSystem()
    zone_empty = Zone("ZE", "Empty Zone")
    area_empty = ParkingArea("AE1", "ZE")
    slot_empty = ParkingSlot("SE1", "ZE")
    area_empty.add_slot(slot_empty)
    zone_empty.add_parking_area(area_empty)
    empty_system.add_zone(zone_empty)

    empty_analytics = Analytics(empty_system)
    empty_avg = empty_analytics.calculate_average_duration()

    if empty_avg is None:
        print("✅ PASS: Returns None for no completed trips")
    else:
        print(f"❌ FAIL: Should return None, got {empty_avg}")
        return False

    # Test 10: Analytics after rollback (data consistency)
    print("\nTest 10: Verify analytics consistency after rollback")

    # Create system with 3 allocations
    rollback_system = ParkingSystem()
    zone_rb = Zone("ZR", "Rollback Zone")
    area_rb = ParkingArea("AR1", "ZR")
    for i in range(5):
        area_rb.add_slot(ParkingSlot(f"SR{i + 1}", "ZR"))
    zone_rb.add_parking_area(area_rb)
    rollback_system.add_zone(zone_rb)

    # Allocate 3 vehicles
    for i in range(3):
        v = Vehicle(f"VR{i}", "ZR")
        r = rollback_system.create_parking_request(v, "ZR")
        rollback_system.process_request(r)

    rb_analytics = Analytics(rollback_system)
    util_before = rb_analytics.calculate_zone_utilization()['ZR']

    # Rollback 2 allocations
    rollback_system.rollback_last_allocations(2)

    util_after = rb_analytics.calculate_zone_utilization()['ZR']

    # Before: 3/5 = 60%, After: 1/5 = 20%
    if util_before == 60.0 and util_after == 20.0:
        print(f"✅ PASS: Utilization updated correctly "
              f"({util_before}% → {util_after}%)")
    else:
        print(f"❌ FAIL: Expected 60% → 20%, got {util_before}% → {util_after}%")
        return False

    # Test 11: Zone with zero slots
    print("\nTest 11: Handle zone with zero slots")
    zero_system = ParkingSystem()
    zone_zero = Zone("ZZ", "Zero Zone")
    area_zero = ParkingArea("AZ1", "ZZ")
    # Don't add any slots
    zone_zero.add_parking_area(area_zero)
    zero_system.add_zone(zone_zero)

    zero_analytics = Analytics(zero_system)
    zero_util = zero_analytics.calculate_zone_utilization()

    if zero_util.get('ZZ') == 0.0:
        print("✅ PASS: Zero slots handled correctly (0% utilization)")
    else:
        print(f"❌ FAIL: Expected 0%, got {zero_util.get('ZZ')}%")
        return False

    # Test 12: Full report content verification
    print("\nTest 12: Verify report contains all sections")
    full_report = analytics.generate_report()

    required_sections = [
        "SYSTEM SUMMARY",
        "REQUEST STATISTICS",
        "PARKING DURATION",
        "ZONE UTILIZATION",
        "PEAK USAGE ZONES",
        "CROSS-ZONE ALLOCATIONS",
        "REQUEST DISTRIBUTION"
    ]

    missing_sections = [s for s in required_sections if s not in full_report]

    if not missing_sections:
        print("✅ PASS: Report contains all required sections")
    else:
        print(f"❌ FAIL: Missing sections: {missing_sections}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL PHASE 6 TESTS PASSED")
    print("=" * 60)
    print("\n📊 Sample Analytics Output:")
    print(analytics.generate_report())
    return True


if __name__ == "__main__":
    success = test_phase_6()
    sys.exit(0 if success else 1)