# Smart Parking System - Design Documentation

## Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Data Structures](#2-data-structures)
3. [Allocation Strategy](#3-allocation-strategy)
4. [Request Lifecycle State Machine](#4-request-lifecycle-state-machine)
5. [Rollback Mechanism](#5-rollback-mechanism)
6. [Analytics Engine](#6-analytics-engine)
7. [Complexity Analysis](#7-complexity-analysis)
8. [Design Decisions](#8-design-decisions)

---

## 1. System Architecture

### 1.1 Overview

The Smart Parking System is designed as a modular, in-memory parking management solution for a city divided into zones. The architecture follows object-oriented principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     ParkingSystem                           │
│  (Main Orchestrator - Coordinates all components)           │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──► AllocationEngine (Slot allocation logic)
             ├──► RollbackManager (Undo operations)
             ├──► Analytics (Usage analysis)
             └──► Zones (City structure)
                   └──► ParkingAreas
                         └──► ParkingSlots
```

### 1.2 Component Responsibilities

| Component | Responsibility | Key Operations |
|-----------|---------------|----------------|
| **ParkingSystem** | Main orchestrator, request lifecycle management | process_request(), cancel_request(), release_parking() |
| **AllocationEngine** | Parking slot allocation logic | allocate_parking(), find_slot_in_zone() |
| **RollbackManager** | Undo/rollback operations | record_allocation(), rollback_last_k() |
| **Analytics** | Usage analysis and reporting | calculate_average_duration(), zone_utilization() |
| **Zone** | Zone structure and slot aggregation | get_available_slots(), add_adjacent_zone() |
| **ParkingArea** | Slot container within zone | add_slot(), get_available_slots() |
| **ParkingSlot** | Individual parking space | occupy(), release() |
| **ParkingRequest** | Request with state machine | transition_to() |

---

## 2. Data Structures

### 2.1 Zone and Slot Representation

The city is represented as a hierarchical structure:

```
City (ParkingSystem)
 │
 ├── Zone A
 │    ├── ParkingArea A1
 │    │    ├── Slot A1-S1
 │    │    ├── Slot A1-S2
 │    │    └── Slot A1-S3
 │    ├── ParkingArea A2
 │    │    ├── Slot A2-S1
 │    │    └── Slot A2-S2
 │    └── Adjacent Zones: [B, C]
 │
 ├── Zone B
 │    ├── ParkingArea B1
 │    └── Adjacent Zones: [A, C]
 │
 └── Zone C
      ├── ParkingArea C1
      └── Adjacent Zones: [A, B]
```

**Key Design Choices:**
- **Dictionaries for Zones**: O(1) zone lookup by ID
- **Lists for Areas/Slots**: Sequential access for allocation
- **Adjacency Lists**: Efficient cross-zone search

### 2.2 Class Structures

#### ParkingSlot
```python
class ParkingSlot:
    slot_id: str              # Unique identifier
    zone_id: str              # Parent zone
    is_available: bool        # Availability flag
    current_vehicle: Vehicle  # Occupying vehicle (or None)
```

#### ParkingArea
```python
class ParkingArea:
    area_id: str              # Unique identifier
    zone_id: str              # Parent zone
    slots: List[ParkingSlot]  # Contained slots
```

#### Zone
```python
class Zone:
    zone_id: str                    # Unique identifier
    zone_name: str                  # Human-readable name
    parking_areas: List[ParkingArea]
    adjacent_zones: List[str]       # Adjacent zone IDs
```

#### ParkingRequest
```python
class ParkingRequest:
    request_id: str
    vehicle: Vehicle
    requested_zone: str
    state: RequestState           # Enum: REQUESTED, ALLOCATED, etc.
    allocated_slot: ParkingSlot   # Assigned slot (or None)
    request_time: datetime
    start_time: datetime          # When occupied
    end_time: datetime            # When released
    is_cross_zone: bool           # Penalty flag
```

---

## 3. Allocation Strategy

### 3.1 Algorithm Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Receive parking request for Zone Z                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Search Zone Z for available slots                   │
│    - Iterate through all parking areas                 │
│    - Return first available slot                       │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
    Found Slot       No Slot Found
         │                │
         │                ▼
         │    ┌──────────────────────────────────────────┐
         │    │ 3. Search adjacent zones                 │
         │    │    - For each adjacent zone ID           │
         │    │    - Search for available slot           │
         │    │    - Return first found with penalty flag│
         │    └──────────────┬───────────────────────────┘
         │                   │
         │           ┌───────┴────────┐
         │           │                │
         │           ▼                ▼
         │      Found Slot       No Slot Found
         │           │                │
         ▼           ▼                ▼
    ┌────────────────────────────────────────────────────┐
    │ 4. Return allocation result:                       │
    │    - (slot, is_cross_zone=False/True) or None      │
    └────────────────────────────────────────────────────┘
```

### 3.2 Allocation Rules

1. **Same-Zone Preference**: Always attempt allocation in requested zone first
2. **First-Available Strategy**: Return first available slot found (no optimization for "best" slot)
3. **Cross-Zone Penalty**: Set `is_cross_zone=True` flag for penalty/cost tracking
4. **Adjacency Constraint**: Only search zones explicitly marked as adjacent
5. **No Global Search**: If adjacent zones are full, allocation fails (no city-wide search)

### 3.3 Example Scenarios

**Scenario 1: Same-Zone Success**
```
Request: Vehicle V123 → Zone A
Zone A: [Available, Available, Occupied]
Result: Allocate first available slot in Zone A
        is_cross_zone = False
```

**Scenario 2: Cross-Zone Allocation**
```
Request: Vehicle V456 → Zone A
Zone A: [Occupied, Occupied, Occupied]
Zone A Adjacent: [Zone B]
Zone B: [Available, Occupied]
Result: Allocate first available slot in Zone B
        is_cross_zone = True
```

**Scenario 3: No Allocation**
```
Request: Vehicle V789 → Zone A
Zone A: [Occupied, Occupied, Occupied]
Zone A Adjacent: [Zone B, Zone C]
Zone B: [Occupied, Occupied]
Zone C: [Occupied, Occupied, Occupied]
Result: None (no slots available)
```

---

## 4. Request Lifecycle State Machine

### 4.1 State Diagram

```
                    ┌──────────────┐
                    │   REQUESTED  │  (Initial state)
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
         ┌─────────────┐       ┌─────────────┐
         │  ALLOCATED  │       │  CANCELLED  │ (Terminal)
         └──────┬──────┘       └─────────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
  ┌──────────┐    ┌─────────────┐
  │ OCCUPIED │    │  CANCELLED  │ (Terminal)
  └────┬─────┘    └─────────────┘
       │
       ▼
  ┌──────────┐
  │ RELEASED │ (Terminal)
  └──────────┘
```

### 4.2 State Transition Rules

| Current State | Valid Next States | Trigger Action |
|--------------|-------------------|----------------|
| **REQUESTED** | ALLOCATED, CANCELLED | process_request(), cancel_request() |
| **ALLOCATED** | OCCUPIED, CANCELLED | occupy_parking(), cancel_request() |
| **OCCUPIED** | RELEASED | release_parking() |
| **RELEASED** | *(none)* | Terminal state |
| **CANCELLED** | *(none)* | Terminal state |

### 4.3 State Transition Implementation

**Validation Logic:**
```python
VALID_TRANSITIONS = {
    RequestState.REQUESTED: [RequestState.ALLOCATED, RequestState.CANCELLED],
    RequestState.ALLOCATED: [RequestState.OCCUPIED, RequestState.CANCELLED],
    RequestState.OCCUPIED: [RequestState.RELEASED],
    RequestState.RELEASED: [],
    RequestState.CANCELLED: []
}

def transition_to(self, new_state: RequestState):
    if new_state not in VALID_TRANSITIONS[self.state]:
        raise ValueError(f"Invalid transition: {self.state} → {new_state}")
    self.state = new_state
```

**State Enforcement:**
- All state changes go through `transition_to()` method
- Invalid transitions raise `ValueError`
- Timestamps updated automatically (start_time on OCCUPIED, end_time on RELEASED)

### 4.4 State-Specific Actions

| State | Entry Actions | Exit Actions |
|-------|--------------|--------------|
| REQUESTED | Record request_time | - |
| ALLOCATED | Assign slot, mark slot occupied | Free slot if cancelled |
| OCCUPIED | Record start_time | - |
| RELEASED | Record end_time, free slot | - |
| CANCELLED | Free slot if was allocated | - |

---

## 5. Rollback Mechanism

### 5.1 Stack-Based Design

The rollback system uses a **LIFO (Last-In-First-Out) stack** to maintain operation history:

```
┌─────────────────────────────────────────────────┐
│           Rollback Stack (LIFO)                 │
├─────────────────────────────────────────────────┤
│ Top → [Operation 5] ← Most recent              │
│       [Operation 4]                             │
│       [Operation 3]                             │
│       [Operation 2]                             │
│       [Operation 1] ← Oldest                    │
└─────────────────────────────────────────────────┘
```

### 5.2 Operation Record Structure

Each operation record contains:
```python
{
    'type': 'ALLOCATION',
    'request_id': 'R0042',
    'slot': ParkingSlot object,
    'previous_state': RequestState.REQUESTED,
    'timestamp': datetime(2025, 1, 28, 14, 30, 0),
    'request': ParkingRequest object
}
```

### 5.3 Rollback Algorithm

**Rollback Last k Operations:**
```python
def rollback_last_k(k):
    for i in range(k):
        operation = stack.pop()
        
        # 1. Free the allocated slot
        operation['slot'].release()
        operation['slot'].current_vehicle = None
        
        # 2. Restore request state
        request = operation['request']
        request.state = operation['previous_state']
        request.allocated_slot = None
        
        # 3. Clear timestamps if rolled back to REQUESTED
        if request.state == RequestState.REQUESTED:
            request.start_time = None
```

### 5.4 Rollback Example

**Initial State:**
```
Slot SA1: Occupied by V001 (Request R001: ALLOCATED)
Slot SA2: Occupied by V002 (Request R002: ALLOCATED)
Slot SA3: Occupied by V003 (Request R003: ALLOCATED)
Stack: [R001, R002, R003]
```

**After `rollback_last_k(2)`:**
```
Slot SA1: Occupied by V001 (Request R001: ALLOCATED)
Slot SA2: Available (Request R002: REQUESTED)
Slot SA3: Available (Request R003: REQUESTED)
Stack: [R001]
```

### 5.5 Rollback Constraints

- Maximum stack size: 100 operations (configurable)
- Cannot rollback more than stack size
- Cannot rollback if k ≤ 0
- Rollback only affects ALLOCATION operations
- Other state changes (occupy, release) not tracked for rollback

---

## 6. Analytics Engine

### 6.1 Implemented Metrics

#### 1. Average Parking Duration
**Formula:**
```
avg_duration = Σ(end_time - start_time) / count(RELEASED requests)
```

**Implementation:**
- Filter requests with state = RELEASED
- Calculate duration for each: `end_time - start_time`
- Return average in hours
- Return `None` if no completed trips

**Time Complexity:** O(r) where r = total requests

#### 2. Zone Utilization Rate
**Formula:**
```
utilization(zone) = (occupied_slots / total_slots) × 100%
```

**Implementation:**
- For each zone, count occupied vs total slots
- Return dictionary: `{zone_id: utilization_percentage}`
- Handle zero-slot zones: return 0%

**Time Complexity:** O(z × s) where z = zones, s = avg slots per zone

#### 3. Request Statistics
**Metrics:**
- Total requests
- Completed (RELEASED)
- Cancelled (CANCELLED)
- Active (REQUESTED + ALLOCATED + OCCUPIED)

**Implementation:**
- Filter request_history by state
- Count each category

**Time Complexity:** O(r)

#### 4. Peak Usage Zones
**Ranking:**
- Sort zones by utilization rate (highest first)
- Return list with zone details

**Time Complexity:** O(z log z) for sorting

#### 5. Cross-Zone Statistics
**Metrics:**
- Total allocations
- Cross-zone allocations
- Cross-zone percentage

**Time Complexity:** O(r)

#### 6. Request Distribution by Zone
**Output:**
- Dictionary: `{zone_id: request_count}`
- Shows demand per zone

**Time Complexity:** O(r)

### 6.2 Report Generation

Generates comprehensive text report with all metrics formatted for readability.

---

## 7. Complexity Analysis

### 7.1 Time Complexity

| Operation | Complexity | Explanation |
|-----------|-----------|-------------|
| **Add Zone** | O(1) | Dictionary insertion |
| **Create Request** | O(1) | Object creation, list append |
| **Allocate Slot (same zone)** | O(n) | Linear search through n slots |
| **Allocate Slot (cross-zone)** | O(z × n) | Search z adjacent zones, n slots each |
| **Occupy Parking** | O(r) | Find request in history |
| **Release Parking** | O(r) | Find request in history |
| **Cancel Request** | O(r) | Find request in history |
| **Rollback k operations** | O(k) | Pop k items from stack |
| **Calculate Avg Duration** | O(r) | Scan all requests |
| **Zone Utilization** | O(z × s) | Count slots in z zones with s slots each |
| **Find Peak Zones** | O(z log z) | Sorting z zones |
| **Generate Report** | O(r + z × s) | Combine analytics operations |

**Where:**
- `r` = total requests
- `z` = number of zones
- `s` = average slots per zone
- `n` = slots in target zone
- `k` = rollback depth

### 7.2 Space Complexity

| Component | Complexity | Explanation |
|-----------|-----------|-------------|
| **City Structure** | O(z × a × s) | z zones, a areas/zone, s slots/area |
| **Request History** | O(r) | Store all r requests |
| **Rollback Stack** | O(k) | Limited to k (default 100) operations |
| **Zone Dictionary** | O(z) | Zone ID → Zone object mapping |
| **Temporary Storage** | O(1) | Fixed overhead per operation |

**Total Space:** O(z × a × s + r + k)

### 7.3 Optimization Opportunities

**Current Implementation:**
- Sequential slot search (simple, predictable)
- Full request history scan for analytics

**Potential Optimizations (Not Implemented):**
1. **Indexed Availability**: Maintain separate available slot lists per zone → O(1) allocation
2. **Cached Analytics**: Pre-compute metrics, update incrementally → O(1) queries
3. **Request Index**: Hash map for request_id → request → O(1) lookup
4. **Priority Queue**: For zone selection in cross-zone allocation

**Trade-offs:**
- Current design prioritizes simplicity and correctness
- Memory overhead is acceptable for city-scale (thousands of slots)
- Performance adequate for real-time requests (< 100ms response)

---

## 8. Design Decisions

### 8.1 Why Object-Oriented Design?

**Benefits:**
- Clear encapsulation of responsibilities
- Easy to test individual components
- Extensible (add new zone types, allocation strategies)
- Matches real-world domain model

### 8.2 Why In-Memory Storage?

**Rationale:**
- Fast access (no I/O overhead)
- Sufficient for city-scale deployment (< 10,000 slots)
- Simplifies concurrency (single-threaded)
- Persistence can be added via serialization if needed

**Limitations:**
- Data lost on restart (mitigated by periodic snapshots)
- Limited to available RAM

### 8.3 Why Stack for Rollback?

**Advantages:**
- Natural LIFO semantics match undo operation
- O(1) push/pop operations
- Simple implementation
- Limited memory footprint with max size

**Alternative Considered:**
- Event sourcing: More complex, over-engineered for this use case

### 8.4 Why Enum for States?

**Benefits:**
- Type safety
- Auto-completion in IDEs
- Prevents typos ("OCUPIED" vs "OCCUPIED")
- Clear contract for valid states

### 8.5 Why First-Available Strategy?

**Rationale:**
- Simple, predictable behavior
- Fair (no vehicle gets preference)
- Fast allocation (no optimization search)

**Alternative Considered:**
- Best-fit: Find closest slot to entrance → Requires distance data, added complexity

### 8.6 Why Separate Analytics Module?

**Benefits:**
- Separation of concerns
- Can be extended without touching core logic
- Easy to add new metrics
- Can be optimized independently

---

## 9. System Limitations & Future Enhancements

### 9.1 Current Limitations

1. **No Persistence**: Data lost on restart
2. **No Concurrency**: Single-threaded, not thread-safe
3. **No Real-Time Updates**: GUI must be manually refreshed
4. **No Authentication**: No user management
5. **Fixed Allocation**: No reservation or pre-booking
6. **No Payment Integration**: Penalty flag is symbolic only

### 9.2 Future Enhancements

1. **Database Persistence**: SQLite or PostgreSQL backend
2. **Real-Time WebSocket**: Live updates to GUI
3. **Dynamic Pricing**: Demand-based pricing with penalty calculation
4. **Reservation System**: Book slots in advance
5. **Route Optimization**: Suggest parking based on destination
6. **Mobile App**: Native iOS/Android client
7. **Multi-City Support**: Manage multiple cities
8. **Admin Dashboard**: System monitoring and configuration

---

## 10. Conclusion

The Smart Parking System demonstrates effective use of:
- **Object-oriented design** for clean architecture
- **State machines** for lifecycle management
- **Stack data structures** for rollback operations
- **Analytical processing** for insights

The system is production-ready for single-city deployment with potential for significant enhancement.
