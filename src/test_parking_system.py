"""
Smart Parking System - Test Suite for Phases 1-2
Tests core data structures and request lifecycle state machine
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle
from src.parking_request import ParkingRequest, RequestState


class TestPhase1DataStructures(unittest.TestCase):
    """Test Phase 1: Core Data Structures"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a zone with parking areas and slots
        self.zone_a = Zone("Z1", "Downtown")

        # Create parking area
        self.area_1 = ParkingArea("A1", "Z1")

        # Create slots
        self.slot_1 = ParkingSlot("S1", "Z1")
        self.slot_2 = ParkingSlot("S2", "Z1")
        self.slot_3 = ParkingSlot("S3", "Z1")

        # Add slots to area
        self.area_1.add_slot(self.slot_1)
        self.area_1.add_slot(self.slot_2)
        self.area_1.add_slot(self.slot_3)

        # Add area to zone
        self.zone_a.add_parking_area(self.area_1)

        # Create vehicle
        self.vehicle = Vehicle("V123", "Z1")

    def test_parking_slot_creation(self):
        """Test 1: ParkingSlot initialization"""
        slot = ParkingSlot("S100", "Z1")
        self.assertEqual(slot.slot_id, "S100")
        self.assertEqual(slot.zone_id, "Z1")
        self.assertTrue(slot.is_available)
        self.assertIsNone(slot.current_vehicle)

    def test_slot_occupy_and_release(self):
        """Test 2: Slot occupation and release"""
        slot = ParkingSlot("S200", "Z1")
        vehicle = Vehicle("V200", "Z1")

        # Occupy slot
        slot.occupy(vehicle)
        self.assertFalse(slot.is_available)
        self.assertEqual(slot.current_vehicle, vehicle)

        # Release slot
        slot.release()
        self.assertTrue(slot.is_available)
        self.assertIsNone(slot.current_vehicle)

    def test_slot_occupy_already_occupied(self):
        """Test 3: Cannot occupy already occupied slot"""
        slot = ParkingSlot("S300", "Z1")
        vehicle1 = Vehicle("V301", "Z1")
        vehicle2 = Vehicle("V302", "Z1")

        slot.occupy(vehicle1)

        # Should raise ValueError
        with self.assertRaises(ValueError):
            slot.occupy(vehicle2)

    def test_parking_area_slot_management(self):
        """Test 4: ParkingArea manages slots correctly"""
        area = ParkingArea("A100", "Z1")

        slot1 = ParkingSlot("S401", "Z1")
        slot2 = ParkingSlot("S402", "Z1")
        slot3 = ParkingSlot("S403", "Z1")

        area.add_slot(slot1)
        area.add_slot(slot2)
        area.add_slot(slot3)

        self.assertEqual(len(area.slots), 3)
        self.assertEqual(len(area.get_available_slots()), 3)

        # Occupy one slot
        slot1.occupy(Vehicle("V400", "Z1"))
        self.assertEqual(len(area.get_available_slots()), 2)

    def test_zone_hierarchy(self):
        """Test 5: Zone contains areas and slots"""
        zone = Zone("Z100", "Test Zone")
        area1 = ParkingArea("A101", "Z100")
        area2 = ParkingArea("A102", "Z100")

        slot1 = ParkingSlot("S501", "Z100")
        slot2 = ParkingSlot("S502", "Z100")
        slot3 = ParkingSlot("S503", "Z100")

        area1.add_slot(slot1)
        area1.add_slot(slot2)
        area2.add_slot(slot3)

        zone.add_parking_area(area1)
        zone.add_parking_area(area2)

        # Check all slots
        all_slots = zone.get_all_slots()
        self.assertEqual(len(all_slots), 3)

        # Check available slots
        available = zone.get_available_slots()
        self.assertEqual(len(available), 3)

    def test_zone_adjacent_zones(self):
        """Test 6: Zone adjacency relationships"""
        zone1 = Zone("Z1", "Zone 1")
        zone1.add_adjacent_zone("Z2")
        zone1.add_adjacent_zone("Z3")

        self.assertEqual(len(zone1.adjacent_zones), 2)
        self.assertIn("Z2", zone1.adjacent_zones)
        self.assertIn("Z3", zone1.adjacent_zones)

        # Adding duplicate should not increase count
        zone1.add_adjacent_zone("Z2")
        self.assertEqual(len(zone1.adjacent_zones), 2)

    def test_vehicle_creation(self):
        """Test 7: Vehicle initialization"""
        vehicle = Vehicle("V999", "Z5")
        self.assertEqual(vehicle.vehicle_id, "V999")
        self.assertEqual(vehicle.preferred_zone, "Z5")


class TestPhase2StateMachine(unittest.TestCase):
    """Test Phase 2: Request Lifecycle State Machine"""

    def setUp(self):
        """Set up test fixtures"""
        self.vehicle = Vehicle("V100", "Z1")

    def test_request_creation(self):
        """Test 8: ParkingRequest initialization"""
        request = ParkingRequest("R001", self.vehicle, "Z1")

        self.assertEqual(request.request_id, "R001")
        self.assertEqual(request.vehicle, self.vehicle)
        self.assertEqual(request.requested_zone, "Z1")
        self.assertEqual(request.state, RequestState.REQUESTED)
        self.assertIsNone(request.allocated_slot)
        self.assertIsNone(request.start_time)
        self.assertIsNone(request.end_time)
        self.assertFalse(request.is_cross_zone)

    def test_valid_state_transitions(self):
        """Test 9: Valid state transitions work correctly"""
        request = ParkingRequest("R002", self.vehicle, "Z1")

        # REQUESTED -> ALLOCATED
        request.transition_to(RequestState.ALLOCATED)
        self.assertEqual(request.state, RequestState.ALLOCATED)

        # ALLOCATED -> OCCUPIED
        request.transition_to(RequestState.OCCUPIED)
        self.assertEqual(request.state, RequestState.OCCUPIED)
        self.assertIsNotNone(request.start_time)

        # OCCUPIED -> RELEASED
        request.transition_to(RequestState.RELEASED)
        self.assertEqual(request.state, RequestState.RELEASED)
        self.assertIsNotNone(request.end_time)

    def test_cancellation_from_requested(self):
        """Test 10: Cancel from REQUESTED state"""
        request = ParkingRequest("R003", self.vehicle, "Z1")

        # REQUESTED -> CANCELLED
        request.transition_to(RequestState.CANCELLED)
        self.assertEqual(request.state, RequestState.CANCELLED)

    def test_cancellation_from_allocated(self):
        """Test 11: Cancel from ALLOCATED state"""
        request = ParkingRequest("R004", self.vehicle, "Z1")

        # REQUESTED -> ALLOCATED
        request.transition_to(RequestState.ALLOCATED)

        # ALLOCATED -> CANCELLED
        request.transition_to(RequestState.CANCELLED)
        self.assertEqual(request.state, RequestState.CANCELLED)

    def test_invalid_state_transition(self):
        """Test 12: Invalid state transitions raise ValueError"""
        request = ParkingRequest("R005", self.vehicle, "Z1")

        # REQUESTED -> OCCUPIED (invalid, must go through ALLOCATED)
        with self.assertRaises(ValueError) as context:
            request.transition_to(RequestState.OCCUPIED)

        self.assertIn("Invalid transition", str(context.exception))

    def test_no_transition_from_terminal_states(self):
        """Test 13: Terminal states (RELEASED, CANCELLED) cannot transition"""
        # Test RELEASED
        request1 = ParkingRequest("R006", self.vehicle, "Z1")
        request1.transition_to(RequestState.ALLOCATED)
        request1.transition_to(RequestState.OCCUPIED)
        request1.transition_to(RequestState.RELEASED)

        # Cannot transition from RELEASED
        with self.assertRaises(ValueError):
            request1.transition_to(RequestState.REQUESTED)

        # Test CANCELLED
        request2 = ParkingRequest("R007", self.vehicle, "Z1")
        request2.transition_to(RequestState.CANCELLED)

        # Cannot transition from CANCELLED
        with self.assertRaises(ValueError):
            request2.transition_to(RequestState.REQUESTED)

    def test_occupied_cannot_go_to_allocated(self):
        """Test 14: OCCUPIED cannot transition back to ALLOCATED"""
        request = ParkingRequest("R008", self.vehicle, "Z1")
        request.transition_to(RequestState.ALLOCATED)
        request.transition_to(RequestState.OCCUPIED)

        # Cannot go back to ALLOCATED
        with self.assertRaises(ValueError):
            request.transition_to(RequestState.ALLOCATED)


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPhase1DataStructures))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2StateMachine))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)