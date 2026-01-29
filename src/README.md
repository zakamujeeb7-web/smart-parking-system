# 🚗 Smart Parking Allocation & Zone Management System

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production-success)

**An intelligent parking management system for smart cities**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation) • [Testing](#testing)

</div>

---

## 📋 Overview

The Smart Parking Allocation & Zone Management System is a Python-based solution for managing city-wide parking resources. It implements zone-based allocation, cross-zone fallback, request lifecycle management with state machines, rollback support, and comprehensive analytics.

### Key Highlights

- ✅ **Multi-Zone Management**: City divided into zones with adjacency relationships
- ✅ **Smart Allocation**: Same-zone preference with cross-zone fallback
- ✅ **State Machine**: Strict request lifecycle enforcement (REQUESTED → ALLOCATED → OCCUPIED → RELEASED)
- ✅ **Rollback Support**: Undo last k allocations with state restoration
- ✅ **Real-Time Analytics**: Usage statistics, utilization rates, and trend analysis
- ✅ **Interactive GUI**: Tkinter-based interface with visual city map
- ✅ **Zero Dependencies**: Uses only Python standard library (Tkinter included)

---

## 🎯 Features

### 1. Zone-Based City Representation
- Hierarchical structure: City → Zones → Parking Areas → Slots
- Configurable zone adjacency for cross-zone allocation
- Support for multiple parking areas per zone

### 2. Intelligent Slot Allocation
- **Same-Zone Preference**: Prioritizes requested zone
- **Cross-Zone Fallback**: Automatically searches adjacent zones when full
- **Penalty Tracking**: Flags cross-zone allocations for billing/analytics
- **First-Available Strategy**: Fair, deterministic allocation

### 3. Request Lifecycle Management
- **State Machine**: Enforces valid state transitions
- **States**: REQUESTED → ALLOCATED → OCCUPIED → RELEASED
- **Cancellation**: Supported from REQUESTED or ALLOCATED states
- **Validation**: Prevents invalid state transitions with exceptions

### 4. Rollback & Undo
- Stack-based operation history (configurable size: default 100)
- Rollback last k allocations
- Automatic slot restoration and state recovery
- Maintains data consistency

### 5. Comprehensive Analytics
- Average parking duration
- Zone utilization rates
- Request distribution by zone
- Peak usage zones ranking
- Cross-zone allocation statistics
- Cancelled vs completed request metrics

### 6. Graphical User Interface
- Visual city map with color-coded slot availability
- Real-time status updates
- Interactive controls for all operations
- Live analytics dashboard
- Recent requests history

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Tkinter (included with Python on most systems)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-parking-system.git
   cd smart-parking-system
   ```

2. **Verify Python version**
   ```bash
   python --version  # Should be 3.8+
   ```

3. **Check Tkinter availability**
   ```bash
   python -m tkinter  # Should open a small test window
   ```

4. **Install optional dependencies** (for enhanced analytics)
   ```bash
   pip install -r requirements.txt  # matplotlib is optional
   ```

### Project Structure

```
smart-parking-system/
├── src/
│   ├── __init__.py
│   ├── zone.py                 # Zone class
│   ├── parking_area.py         # Parking area container
│   ├── parking_slot.py         # Individual slot
│   ├── vehicle.py              # Vehicle class
│   ├── parking_request.py      # Request with state machine
│   ├── allocation_engine.py    # Allocation logic
│   ├── rollback_manager.py     # Rollback functionality
│   ├── parking_system.py       # Main system orchestrator
│   ├── analytics.py            # Analytics engine
│   └── gui.py                  # Tkinter GUI
├── tests/
│   ├── __init__.py
│   ├── test_parking_system.py  # Comprehensive test suite
│   ├── test_phase3.py          # Allocation tests
│   ├── test_phase4.py          # Rollback tests
│   ├── test_phase5.py          # Integration tests
│   └── test_phase6.py          # Analytics tests
├── docs/
│   └── design.md               # System design documentation
├── main.py                     # Entry point
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── development.md              # Development roadmap
```

---

## 💻 Usage

### Running the GUI Application

```bash
python main.py
```

This launches the graphical interface with:
- **Left Panel**: Controls for requesting, occupying, releasing, and cancelling parking
- **Center Panel**: Visual city map showing zone layouts and slot status
- **Right Panel**: Real-time analytics and statistics

### GUI Operations

#### 1. Request Parking
1. Enter Vehicle ID (e.g., "V123")
2. Select preferred zone from dropdown
3. Click "🅿️ Request Parking"
4. System allocates slot and shows confirmation

#### 2. Occupy Parking (Vehicle Arrives)
1. Enter Vehicle ID
2. Click "✅ Occupy Parking"
3. Request transitions to OCCUPIED state

#### 3. Release Parking (Vehicle Leaves)
1. Enter Vehicle ID
2. Click "🚪 Release Parking"
3. Slot becomes available, duration recorded

#### 4. Cancel Request
1. Enter Vehicle ID
2. Click "❌ Cancel Request"
3. Slot freed if allocated, request cancelled

#### 5. Rollback Operations
1. Enter number of operations to undo (e.g., "3")
2. Click "⏪ Rollback"
3. Last k allocations reversed

### Programmatic Usage

```python
from src.parking_system import ParkingSystem
from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle

# Initialize system
system = ParkingSystem()

# Create zone
zone_a = Zone("ZA", "Downtown")
area_a1 = ParkingArea("AA1", "ZA")

# Add slots
for i in range(5):
    slot = ParkingSlot(f"SA{i+1}", "ZA")
    area_a1.add_slot(slot)

zone_a.add_parking_area(area_a1)
system.add_zone(zone_a)

# Request parking
vehicle = Vehicle("V001", "ZA")
request = system.create_parking_request(vehicle, "ZA")
success = system.process_request(request)

if success:
    print(f"Allocated: {request.allocated_slot.slot_id}")
    
# Occupy parking
system.occupy_parking(request.request_id)

# Release parking
system.release_parking(request.request_id)

# Get analytics
from src.analytics import Analytics
analytics = Analytics(system)
print(analytics.generate_report())
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run complete test suite
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python tests/test_parking_system.py
```

### Test Coverage

The project includes **50+ test cases** covering:

| Test Category | Tests | Coverage |
|--------------|-------|----------|
| Core Data Structures | 7 | Zone, Area, Slot, Vehicle creation and management |
| State Machine | 7 | All valid and invalid state transitions |
| Allocation Engine | 5 | Same-zone, cross-zone, no-slots scenarios |
| Rollback Manager | 8 | Stack operations, state restoration |
| System Integration | 15 | End-to-end workflows |
| Analytics | 12 | All metrics and edge cases |

### Sample Test Output

```
======================================================================
TEST SUMMARY
======================================================================
Tests Run: 54
Successes: 54
Failures: 0
Errors: 0
======================================================================
```

---

## 📊 Analytics & Reporting

### Available Metrics

1. **Average Parking Duration**
   - Mean time vehicles spend parked
   - Calculated from RELEASED requests only

2. **Zone Utilization Rate**
   - Percentage of occupied slots per zone
   - Real-time calculation

3. **Request Statistics**
   - Total, completed, cancelled, active requests
   - Breakdown by state

4. **Peak Usage Zones**
   - Zones ranked by utilization
   - Identifies high-demand areas

5. **Cross-Zone Allocations**
   - Percentage of requests allocated outside requested zone
   - Helps optimize zone capacity

6. **Request Distribution**
   - Demand per zone
   - Useful for capacity planning

### Generate Report

```python
from src.analytics import Analytics

analytics = Analytics(parking_system)
report = analytics.generate_report()
print(report)
```

**Sample Output:**
```
============================================================
PARKING SYSTEM ANALYTICS REPORT
============================================================
Generated: 2025-01-28 14:30:00

SYSTEM SUMMARY
------------------------------------------------------------
Total Zones: 4
Total Slots: 18
Available Slots: 10
Occupied Slots: 8

REQUEST STATISTICS
------------------------------------------------------------
Total Requests: 25
Completed: 15
Cancelled: 3
Active: 7

PARKING DURATION
------------------------------------------------------------
Average Duration: 2.3 hours

ZONE UTILIZATION
------------------------------------------------------------
Downtown (ZA): 66.67%
Uptown (ZB): 50.00%
Midtown (ZC): 40.00%
Eastside (ZD): 33.33%
============================================================
```

---

## 📖 Documentation

### Design Documentation
- **Full System Design**: [docs/design.md](docs/design.md)
  - Architecture overview
  - Data structures
  - Algorithms and complexity analysis
  - State machine diagrams
  - Design decisions and trade-offs

### API Documentation
All classes and methods include docstrings:

```python
>>> from src.parking_system import ParkingSystem
>>> help(ParkingSystem.process_request)

process_request(self, request: ParkingRequest) -> bool
    Process a parking request and allocate a slot
    
    Args:
        request: ParkingRequest to process
    
    Returns:
        True if allocation successful, False otherwise
```

---

## ⚙️ Configuration

### Sample City Setup

```python
# Create 4-zone city with adjacencies

zone_a = Zone("ZA", "Downtown")
zone_b = Zone("ZB", "Uptown")
zone_c = Zone("ZC", "Midtown")
zone_d = Zone("ZD", "Eastside")

# Set adjacencies
zone_a.add_adjacent_zone("ZB")
zone_a.add_adjacent_zone("ZC")
zone_b.add_adjacent_zone("ZA")
zone_b.add_adjacent_zone("ZC")
zone_c.add_adjacent_zone("ZA")
zone_c.add_adjacent_zone("ZB")
zone_c.add_adjacent_zone("ZD")
zone_d.add_adjacent_zone("ZC")

# Add to system
system.add_zone(zone_a)
system.add_zone(zone_b)
system.add_zone(zone_c)
system.add_zone(zone_d)
```

### Rollback Stack Size

```python
from src.rollback_manager import RollbackManager

# Default: 100 operations
rollback_mgr = RollbackManager(max_stack_size=100)

# Custom size
rollback_mgr = RollbackManager(max_stack_size=50)
```

---

## 🔧 Development

### Adding a New Zone

```python
# 1. Create zone
new_zone = Zone("ZE", "Westside")

# 2. Create parking areas
area_e1 = ParkingArea("AE1", "ZE")
area_e2 = ParkingArea("AE2", "ZE")

# 3. Add slots
for i in range(10):
    area_e1.add_slot(ParkingSlot(f"SE1-{i}", "ZE"))
for i in range(8):
    area_e2.add_slot(ParkingSlot(f"SE2-{i}", "ZE"))

# 4. Add areas to zone
new_zone.add_parking_area(area_e1)
new_zone.add_parking_area(area_e2)

# 5. Set adjacencies
new_zone.add_adjacent_zone("ZD")
zone_d.add_adjacent_zone("ZE")  # Bidirectional

# 6. Add to system
system.add_zone(new_zone)
```

### Extending Analytics

```python
# Add custom metric to Analytics class

def calculate_peak_hours(self) -> Dict[int, int]:
    """Calculate parking requests by hour of day"""
    hour_counts = {}
    
    for request in self.parking_system.request_history:
        hour = request.request_time.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    return hour_counts
```

---

## 🤝 Contributing

### Development Phases
The project was developed in 9 phases (see `development.md`):
1. Core Data Structures
2. Request Lifecycle & State Machine
3. Allocation Engine
4. Rollback Manager
5. System Integration
6. Analytics Module
7. GUI Development
8. Testing
9. Documentation

### Code Standards
- Follow PEP 8 style guide
- Include docstrings for all public methods
- Add type hints where applicable
- Write tests for new features
- Update documentation

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Built as a DSA semester project
- Implements concepts: Arrays, Lists, Stacks, State Machines, Analytics
- Focused on real-world resource allocation modeling

---

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Refer to design documentation: `docs/design.md`
- Run tests to verify setup: `python -m pytest tests/`

---

<div align="center">

**Made with ❤️ for Smart Cities**

[⬆ Back to Top](#-smart-parking-allocation--zone-management-system)

</div>
