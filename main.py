"""
Smart Parking System - Main Entry Point
"""

from src.parking_system import ParkingSystem
from src.gui import ParkingGUI


def main():
    """Main entry point"""
    # Initialize system
    parking_system = ParkingSystem()

    # Launch GUI
    app = ParkingGUI(parking_system)
    app.run()


if __name__ == "__main__":
    main()
