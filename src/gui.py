"""
GUI Module - Graphical User Interface for Smart Parking System
Provides interactive controls and visual feedback for parking management
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
from src.parking_system import ParkingSystem
from src.zone import Zone
from src.parking_area import ParkingArea
from src.parking_slot import ParkingSlot
from src.vehicle import Vehicle
from src.parking_request import RequestState
from src.analytics import Analytics


class ParkingGUI:
    """Main GUI Application for Smart Parking System"""

    # Color scheme
    COLOR_AVAILABLE = "#4CAF50"  # Green
    COLOR_OCCUPIED = "#F44336"   # Red
    COLOR_BG = "#ECEFF1"         # Light gray
    COLOR_PANEL = "#FFFFFF"      # White
    COLOR_ACCENT = "#2196F3"     # Blue

    def __init__(self, parking_system: ParkingSystem):
        """
        Initialize GUI

        Args:
            parking_system: ParkingSystem instance to manage
        """
        self.system = parking_system
        self.analytics = Analytics(parking_system)

        # Initialize with sample data if empty
        if not self.system.zones:
            self._initialize_sample_city()

        # Create main window
        self.root = tk.Tk()
        self.root.title("Smart Parking Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg=self.COLOR_BG)

        # Create UI components
        self._create_header()
        self._create_main_panels()
        self._create_footer()

        # Initial refresh
        self.refresh_display()

    def _initialize_sample_city(self):
        """Create sample city with zones for demonstration"""
        # Zone A (Downtown) - 6 slots
        zone_a = Zone("ZA", "Downtown")
        area_a1 = ParkingArea("AA1", "ZA")
        area_a2 = ParkingArea("AA2", "ZA")
        for i in range(3):
            area_a1.add_slot(ParkingSlot(f"SA{i + 1}", "ZA"))
            area_a2.add_slot(ParkingSlot(f"SA{i + 4}", "ZA"))
        zone_a.add_parking_area(area_a1)
        zone_a.add_parking_area(area_a2)

        # Zone B (Uptown) - 4 slots
        zone_b = Zone("ZB", "Uptown")
        area_b1 = ParkingArea("AB1", "ZB")
        for i in range(4):
            area_b1.add_slot(ParkingSlot(f"SB{i + 1}", "ZB"))
        zone_b.add_parking_area(area_b1)

        # Zone C (Midtown) - 5 slots
        zone_c = Zone("ZC", "Midtown")
        area_c1 = ParkingArea("AC1", "ZC")
        for i in range(5):
            area_c1.add_slot(ParkingSlot(f"SC{i + 1}", "ZC"))
        zone_c.add_parking_area(area_c1)

        # Zone D (Eastside) - 3 slots
        zone_d = Zone("ZD", "Eastside")
        area_d1 = ParkingArea("AD1", "ZD")
        for i in range(3):
            area_d1.add_slot(ParkingSlot(f"SD{i + 1}", "ZD"))
        zone_d.add_parking_area(area_d1)

        # Set up adjacencies
        zone_a.add_adjacent_zone("ZB")
        zone_a.add_adjacent_zone("ZC")
        zone_b.add_adjacent_zone("ZA")
        zone_b.add_adjacent_zone("ZC")
        zone_c.add_adjacent_zone("ZA")
        zone_c.add_adjacent_zone("ZB")
        zone_c.add_adjacent_zone("ZD")
        zone_d.add_adjacent_zone("ZC")

        # Add zones to system
        self.system.add_zone(zone_a)
        self.system.add_zone(zone_b)
        self.system.add_zone(zone_c)
        self.system.add_zone(zone_d)

    def _create_header(self):
        """Create header with title"""
        header_frame = tk.Frame(self.root, bg=self.COLOR_ACCENT, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title = tk.Label(
            header_frame,
            text="🚗 Smart Parking Management System",
            font=("Arial", 18, "bold"),
            bg=self.COLOR_ACCENT,
            fg="white"
        )
        title.pack(expand=True)

    def _create_main_panels(self):
        """Create the three main panels: Controls, City Map, Analytics"""
        main_container = tk.Frame(self.root, bg=self.COLOR_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel - Controls (25%)
        self.control_panel = tk.Frame(main_container, bg=self.COLOR_PANEL, relief=tk.RAISED, bd=2)
        self.control_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        self.control_panel.config(width=350)
        self._create_control_panel()

        # Center Panel - City Map (50%)
        self.map_panel = tk.Frame(main_container, bg=self.COLOR_PANEL, relief=tk.RAISED, bd=2)
        self.map_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self._create_map_panel()

        # Right Panel - Analytics (25%)
        self.analytics_panel = tk.Frame(main_container, bg=self.COLOR_PANEL, relief=tk.RAISED, bd=2)
        self.analytics_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        self.analytics_panel.config(width=350)
        self._create_analytics_panel()

    def _create_control_panel(self):
        """Create control panel with input forms and action buttons"""
        # Title
        tk.Label(
            self.control_panel,
            text="Controls",
            font=("Arial", 16, "bold"),
            bg=self.COLOR_PANEL
        ).pack(pady=10)

        # Vehicle ID input
        tk.Label(self.control_panel, text="Vehicle ID:", bg=self.COLOR_PANEL).pack(pady=(10, 0))
        self.vehicle_id_entry = tk.Entry(self.control_panel, width=30)
        self.vehicle_id_entry.pack(pady=5)

        # Zone selection
        tk.Label(self.control_panel, text="Select Zone:", bg=self.COLOR_PANEL).pack(pady=(10, 0))
        self.zone_var = tk.StringVar()
        zone_ids = list(self.system.zones.keys())
        self.zone_var.set(zone_ids[0] if zone_ids else "")
        self.zone_dropdown = ttk.Combobox(
            self.control_panel,
            textvariable=self.zone_var,
            values=zone_ids,
            state="readonly",
            width=27
        )
        self.zone_dropdown.pack(pady=5)

        # Action Buttons
        btn_frame = tk.Frame(self.control_panel, bg=self.COLOR_PANEL)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="🅿️ Request Parking",
            command=self.request_parking,
            bg=self.COLOR_ACCENT,
            fg="white",
            width=20,
            height=2
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="✅ Occupy Parking",
            command=self.occupy_parking,
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="🚪 Release Parking",
            command=self.release_parking,
            bg="#FF9800",
            fg="white",
            width=20,
            height=2
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="❌ Cancel Request",
            command=self.cancel_request,
            bg="#F44336",
            fg="white",
            width=20,
            height=2
        ).pack(pady=5)

        # Rollback section
        tk.Label(self.control_panel, text="Rollback Count:", bg=self.COLOR_PANEL).pack(pady=(20, 0))
        self.rollback_entry = tk.Entry(self.control_panel, width=30)
        self.rollback_entry.insert(0, "1")
        self.rollback_entry.pack(pady=5)

        tk.Button(
            self.control_panel,
            text="⏪ Rollback",
            command=self.rollback_operations,
            bg="#9C27B0",
            fg="white",
            width=20,
            height=2
        ).pack(pady=5)

        # Recent requests display
        tk.Label(
            self.control_panel,
            text="Recent Requests:",
            font=("Arial", 12, "bold"),
            bg=self.COLOR_PANEL
        ).pack(pady=(20, 5))

        self.recent_list = tk.Listbox(self.control_panel, height=8, width=35)
        self.recent_list.pack(pady=5, padx=10)

    def _create_map_panel(self):
        """Create city map visualization panel"""
        # Title
        tk.Label(
            self.map_panel,
            text="City Parking Map",
            font=("Arial", 16, "bold"),
            bg=self.COLOR_PANEL
        ).pack(pady=10)

        # Canvas for zone visualization
        self.canvas = tk.Canvas(self.map_panel, bg="white", height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Legend
        legend_frame = tk.Frame(self.map_panel, bg=self.COLOR_PANEL)
        legend_frame.pack(pady=5)

        tk.Label(legend_frame, text="🟢 Available", bg=self.COLOR_PANEL).pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text="🔴 Occupied", bg=self.COLOR_PANEL).pack(side=tk.LEFT, padx=10)

    def _create_analytics_panel(self):
        """Create analytics display panel"""
        # Title
        tk.Label(
            self.analytics_panel,
            text="Analytics",
            font=("Arial", 16, "bold"),
            bg=self.COLOR_PANEL
        ).pack(pady=10)

        # Statistics display (scrollable text)
        self.stats_display = scrolledtext.ScrolledText(
            self.analytics_panel,
            width=40,
            height=35,
            font=("Courier", 9)
        )
        self.stats_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Refresh button
        tk.Button(
            self.analytics_panel,
            text="🔄 Refresh Stats",
            command=self.refresh_analytics,
            bg=self.COLOR_ACCENT,
            fg="white",
            width=20
        ).pack(pady=10)

    def _create_footer(self):
        """Create footer with system info"""
        footer_frame = tk.Frame(self.root, bg=self.COLOR_BG, height=30)
        footer_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            footer_frame,
            text="System Ready",
            bg=self.COLOR_BG,
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

    def draw_city_map(self):
        """Draw visual representation of zones and slots"""
        self.canvas.delete("all")

        zones = list(self.system.zones.values())
        if not zones:
            return

        # Calculate grid layout
        cols = 2
        rows = (len(zones) + 1) // 2

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Use default size if canvas not rendered yet
        if canvas_width <= 1:
            canvas_width = 600
            canvas_height = 500

        zone_width = (canvas_width - 60) // cols
        zone_height = max(200, (canvas_height - 60) // rows)

        for idx, zone in enumerate(zones):
            row = idx // cols
            col = idx % cols

            x = 30 + col * zone_width
            y = 30 + row * zone_height

            # Draw zone container
            self.canvas.create_rectangle(
                x, y, x + zone_width - 20, y + zone_height - 20,
                outline=self.COLOR_ACCENT,
                width=2
            )

            # Zone title
            self.canvas.create_text(
                x + (zone_width - 20) / 2,
                y + 15,
                text=f"{zone.zone_name} ({zone.zone_id})",
                font=("Arial", 12, "bold")
            )

            # Draw slots
            slots = zone.get_all_slots()
            slot_size = 30
            slots_per_row = max(1, (zone_width - 40) // (slot_size + 5))

            for slot_idx, slot in enumerate(slots):
                slot_row = slot_idx // slots_per_row
                slot_col = slot_idx % slots_per_row

                slot_x = x + 10 + slot_col * (slot_size + 5)
                slot_y = y + 40 + slot_row * (slot_size + 5)

                color = self.COLOR_AVAILABLE if slot.is_available else self.COLOR_OCCUPIED

                self.canvas.create_rectangle(
                    slot_x, slot_y,
                    slot_x + slot_size, slot_y + slot_size,
                    fill=color,
                    outline="black"
                )

                # Slot ID
                self.canvas.create_text(
                    slot_x + slot_size / 2,
                    slot_y + slot_size / 2,
                    text=slot.slot_id[-2:],  # Show last 2 chars
                    font=("Arial", 8)
                )

            # Zone stats
            available = len(zone.get_available_slots())
            total = len(slots)
            self.canvas.create_text(
                x + (zone_width - 20) / 2,
                y + zone_height - 35,  # Moved up 5 pixels
                text=f"{available}/{total} available",
                font=("Arial", 10)
            )

    def update_recent_requests(self):
        """Update recent requests listbox"""
        self.recent_list.delete(0, tk.END)

        # Show last 10 requests
        recent = self.system.request_history[-10:]
        for req in reversed(recent):
            status_icon = {
                RequestState.REQUESTED: "⏳",
                RequestState.ALLOCATED: "📍",
                RequestState.OCCUPIED: "🚗",
                RequestState.RELEASED: "✅",
                RequestState.CANCELLED: "❌"
            }.get(req.state, "•")

            text = f"{status_icon} {req.vehicle.vehicle_id} @{req.requested_zone} [{req.state.value}]"
            self.recent_list.insert(tk.END, text)

    def refresh_analytics(self):
        """Refresh analytics display"""
        self.stats_display.delete(1.0, tk.END)
        report = self.analytics.generate_report()
        self.stats_display.insert(1.0, report)

    def refresh_display(self):
        """Refresh all display components"""
        self.draw_city_map()
        self.update_recent_requests()
        self.refresh_analytics()

    # Action Handlers
    def request_parking(self):
        """Handle parking request"""
        vehicle_id = self.vehicle_id_entry.get().strip()
        zone_id = self.zone_var.get()

        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a Vehicle ID")
            return

        if not zone_id:
            messagebox.showerror("Error", "Please select a zone")
            return

        # Create vehicle and request
        vehicle = Vehicle(vehicle_id, zone_id)
        request = self.system.create_parking_request(vehicle, zone_id)

        # Process request
        success = self.system.process_request(request)

        if success:
            slot_info = f"Slot: {request.allocated_slot.slot_id}"
            if request.is_cross_zone:
                slot_info += f" (Cross-zone: {request.allocated_slot.zone_id})"

            messagebox.showinfo(
                "Success",
                f"Parking allocated!\nRequest ID: {request.request_id}\n{slot_info}"
            )
            self.vehicle_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Error",
                f"No parking available in {zone_id} or adjacent zones"
            )

        self.refresh_display()

    def occupy_parking(self):
        """Handle occupy parking action"""
        vehicle_id = self.vehicle_id_entry.get().strip()

        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a Vehicle ID")
            return

        # Find allocated request for this vehicle
        request = None
        for req in self.system.request_history:
            if (req.vehicle.vehicle_id == vehicle_id and
                req.state == RequestState.ALLOCATED):
                request = req
                break

        if not request:
            messagebox.showerror(
                "Error",
                f"No allocated parking found for vehicle {vehicle_id}"
            )
            return

        try:
            self.system.occupy_parking(request.request_id)
            messagebox.showinfo(
                "Success",
                f"Parking occupied by {vehicle_id}\nSlot: {request.allocated_slot.slot_id}"
            )
            self.vehicle_id_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

        self.refresh_display()

    def release_parking(self):
        """Handle release parking action"""
        vehicle_id = self.vehicle_id_entry.get().strip()

        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a Vehicle ID")
            return

        # Find occupied request for this vehicle
        request = None
        for req in self.system.request_history:
            if (req.vehicle.vehicle_id == vehicle_id and
                req.state == RequestState.OCCUPIED):
                request = req
                break

        if not request:
            messagebox.showerror(
                "Error",
                f"No occupied parking found for vehicle {vehicle_id}"
            )
            return

        try:
            self.system.release_parking(request.request_id)
            messagebox.showinfo(
                "Success",
                f"Parking released by {vehicle_id}"
            )
            self.vehicle_id_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

        self.refresh_display()

    def cancel_request(self):
        """Handle cancel request action"""
        vehicle_id = self.vehicle_id_entry.get().strip()

        if not vehicle_id:
            messagebox.showerror("Error", "Please enter a Vehicle ID")
            return

        # Find cancellable request for this vehicle
        request = None
        for req in reversed(self.system.request_history):
            if (req.vehicle.vehicle_id == vehicle_id and
                req.state in [RequestState.REQUESTED, RequestState.ALLOCATED]):
                request = req
                break

        if not request:
            messagebox.showerror(
                "Error",
                f"No cancellable request found for vehicle {vehicle_id}"
            )
            return

        try:
            self.system.cancel_request(request.request_id)
            messagebox.showinfo(
                "Success",
                f"Request {request.request_id} cancelled"
            )
            self.vehicle_id_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

        self.refresh_display()

    def rollback_operations(self):
        """Handle rollback action"""
        try:
            k = int(self.rollback_entry.get())
            if k <= 0:
                raise ValueError("Count must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid rollback count: {e}")
            return

        try:
            rolled_back = self.system.rollback_last_allocations(k)
            messagebox.showinfo(
                "Success",
                f"Rolled back {len(rolled_back)} operations:\n" +
                ", ".join(rolled_back)
            )
        except ValueError as e:
            messagebox.showerror("Error", str(e))

        self.refresh_display()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()