"""
Analytics Module - Provides trip history analysis and parking usage analytics
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.parking_request import ParkingRequest, RequestState


class Analytics:
    """
    Analytics engine for parking system
    Provides insights into parking usage, duration, and zone utilization
    """

    def __init__(self, parking_system):
        """
        Initialize Analytics

        Args:
            parking_system: ParkingSystem instance to analyze
        """
        self.parking_system = parking_system

    def calculate_average_duration(self) -> Optional[float]:
        """
        Calculate average parking duration for completed trips

        Returns:
            Average duration in hours, or None if no completed trips
        """
        completed_requests = [
            req for req in self.parking_system.request_history
            if req.state == RequestState.RELEASED and 
            req.start_time and req.end_time
        ]

        if not completed_requests:
            return None

        total_duration = timedelta()
        for req in completed_requests:
            duration = req.end_time - req.start_time
            total_duration += duration

        # Convert to hours
        average_seconds = total_duration.total_seconds() / len(completed_requests)
        average_hours = average_seconds / 3600

        return round(average_hours, 2)

    def calculate_zone_utilization(self) -> Dict[str, float]:
        """
        Calculate utilization rate for each zone

        Returns:
            Dictionary {zone_id: utilization_percentage}
        """
        utilization = {}

        for zone_id, zone in self.parking_system.zones.items():
            all_slots = zone.get_all_slots()
            if not all_slots:
                utilization[zone_id] = 0.0
                continue

            occupied_count = len([s for s in all_slots if not s.is_available])
            utilization_rate = (occupied_count / len(all_slots)) * 100
            utilization[zone_id] = round(utilization_rate, 2)

        return utilization

    def get_cancelled_vs_completed(self) -> Dict[str, int]:
        """
        Get count of cancelled vs completed requests

        Returns:
            Dictionary with counts:
            {
                'completed': count,
                'cancelled': count,
                'active': count (requested/allocated/occupied)
            }
        """
        completed = len([
            req for req in self.parking_system.request_history
            if req.state == RequestState.RELEASED
        ])

        cancelled = len([
            req for req in self.parking_system.request_history
            if req.state == RequestState.CANCELLED
        ])

        active = len([
            req for req in self.parking_system.request_history
            if req.state in [
                RequestState.REQUESTED,
                RequestState.ALLOCATED,
                RequestState.OCCUPIED
            ]
        ])

        return {
            'completed': completed,
            'cancelled': cancelled,
            'active': active,
            'total': len(self.parking_system.request_history)
        }

    def find_peak_usage_zones(self) -> List[Dict]:
        """
        Find zones with highest occupation/usage

        Returns:
            List of zones sorted by usage (highest first)
            Each entry: {
                'zone_id': str,
                'zone_name': str,
                'utilization': float,
                'occupied_slots': int,
                'total_slots': int
            }
        """
        zone_stats = []

        for zone_id, zone in self.parking_system.zones.items():
            all_slots = zone.get_all_slots()
            if not all_slots:
                continue

            occupied_count = len([s for s in all_slots if not s.is_available])
            utilization = (occupied_count / len(all_slots)) * 100

            zone_stats.append({
                'zone_id': zone_id,
                'zone_name': zone.zone_name,
                'utilization': round(utilization, 2),
                'occupied_slots': occupied_count,
                'total_slots': len(all_slots)
            })

        # Sort by utilization (highest first)
        zone_stats.sort(key=lambda x: x['utilization'], reverse=True)

        return zone_stats

    def get_cross_zone_statistics(self) -> Dict:
        """
        Get statistics on cross-zone allocations

        Returns:
            Dictionary with cross-zone allocation stats
        """
        allocated_requests = [
            req for req in self.parking_system.request_history
            if req.state in [
                RequestState.ALLOCATED,
                RequestState.OCCUPIED,
                RequestState.RELEASED
            ]
        ]

        if not allocated_requests:
            return {
                'total_allocations': 0,
                'cross_zone_allocations': 0,
                'cross_zone_percentage': 0.0
            }

        cross_zone_count = len([
            req for req in allocated_requests
            if req.is_cross_zone
        ])

        return {
            'total_allocations': len(allocated_requests),
            'cross_zone_allocations': cross_zone_count,
            'cross_zone_percentage': round(
                (cross_zone_count / len(allocated_requests)) * 100, 2
            )
        }

    def get_zone_request_distribution(self) -> Dict[str, int]:
        """
        Get distribution of requests by zone

        Returns:
            Dictionary {zone_id: request_count}
        """
        distribution = {}

        for zone_id in self.parking_system.zones.keys():
            count = len([
                req for req in self.parking_system.request_history
                if req.requested_zone == zone_id
            ])
            distribution[zone_id] = count

        return distribution

    def generate_report(self) -> str:
        """
        Generate comprehensive analytics report

        Returns:
            Formatted string report
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("PARKING SYSTEM ANALYTICS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # System summary
        summary = self.parking_system.get_system_summary()
        report_lines.append("SYSTEM SUMMARY")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Zones: {summary['total_zones']}")
        report_lines.append(f"Total Slots: {summary['total_slots']}")
        report_lines.append(f"Available Slots: {summary['available_slots']}")
        report_lines.append(f"Occupied Slots: {summary['occupied_slots']}")
        report_lines.append("")

        # Request statistics
        req_stats = self.get_cancelled_vs_completed()
        report_lines.append("REQUEST STATISTICS")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Requests: {req_stats['total']}")
        report_lines.append(f"Completed: {req_stats['completed']}")
        report_lines.append(f"Cancelled: {req_stats['cancelled']}")
        report_lines.append(f"Active: {req_stats['active']}")
        report_lines.append("")

        # Average duration
        avg_duration = self.calculate_average_duration()
        report_lines.append("PARKING DURATION")
        report_lines.append("-" * 60)
        if avg_duration is not None:
            report_lines.append(f"Average Duration: {avg_duration} hours")
        else:
            report_lines.append("Average Duration: N/A (no completed trips)")
        report_lines.append("")

        # Zone utilization
        utilization = self.calculate_zone_utilization()
        report_lines.append("ZONE UTILIZATION")
        report_lines.append("-" * 60)
        for zone_id, util_rate in utilization.items():
            zone_name = self.parking_system.zones[zone_id].zone_name
            report_lines.append(f"{zone_name} ({zone_id}): {util_rate}%")
        report_lines.append("")

        # Peak usage zones
        peak_zones = self.find_peak_usage_zones()
        report_lines.append("PEAK USAGE ZONES (Top 3)")
        report_lines.append("-" * 60)
        for i, zone in enumerate(peak_zones[:3], 1):
            report_lines.append(
                f"{i}. {zone['zone_name']} ({zone['zone_id']}): "
                f"{zone['utilization']}% "
                f"({zone['occupied_slots']}/{zone['total_slots']} slots)"
            )
        report_lines.append("")

        # Cross-zone statistics
        cross_zone = self.get_cross_zone_statistics()
        report_lines.append("CROSS-ZONE ALLOCATIONS")
        report_lines.append("-" * 60)
        report_lines.append(f"Total Allocations: {cross_zone['total_allocations']}")
        report_lines.append(
            f"Cross-Zone: {cross_zone['cross_zone_allocations']} "
            f"({cross_zone['cross_zone_percentage']}%)"
        )
        report_lines.append("")

        # Request distribution
        distribution = self.get_zone_request_distribution()
        report_lines.append("REQUEST DISTRIBUTION BY ZONE")
        report_lines.append("-" * 60)
        for zone_id, count in distribution.items():
            zone_name = self.parking_system.zones[zone_id].zone_name
            report_lines.append(f"{zone_name} ({zone_id}): {count} requests")
        report_lines.append("")

        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def export_to_dict(self) -> Dict:
        """
        Export all analytics as a dictionary for programmatic use

        Returns:
            Dictionary containing all analytics data
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'system_summary': self.parking_system.get_system_summary(),
            'average_duration_hours': self.calculate_average_duration(),
            'zone_utilization': self.calculate_zone_utilization(),
            'request_statistics': self.get_cancelled_vs_completed(),
            'peak_usage_zones': self.find_peak_usage_zones(),
            'cross_zone_statistics': self.get_cross_zone_statistics(),
            'request_distribution': self.get_zone_request_distribution()
        }
