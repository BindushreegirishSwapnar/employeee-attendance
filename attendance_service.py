"""
Attendance Service
Handles all attendance-related calculations and queries.
"""
from config import config


def calculate_attendance_percentage(days_present: float, total_working_days: float) -> float:
    """
    Calculate attendance percentage.

    Formula: (days_present / total_working_days) * 100
    Returns 0.0 safely on division-by-zero.
    Rounded to 2 decimal places.
    """
    if total_working_days <= 0:
        return 0.0
    percentage = (days_present / total_working_days) * 100.0
    return round(percentage, 2)


def get_attendance_status(attendance_percentage: float) -> str:
    """
    Return human-readable attendance status based on the configured threshold.

    Below ATTENDANCE_THRESHOLD  → 'Below Threshold'
    At or above threshold       → 'Good Attendance'
    """
    if attendance_percentage < config.ATTENDANCE_THRESHOLD:
        return 'Below Threshold'
    return 'Good Attendance'


def is_below_threshold(attendance_percentage: float) -> bool:
    """Return True if the employee is below the attendance threshold."""
    return attendance_percentage < config.ATTENDANCE_THRESHOLD


def get_employees_below_threshold(employees):
    """
    Filter a list of Employee ORM objects and return only those
    whose attendance is below the configured threshold.
    """
    return [e for e in employees if is_below_threshold(e.attendance_percentage)]


def get_attendance_summary(employees):
    """
    Given a list of Employee ORM objects, return a dict with:
        - total_employees
        - average_attendance
        - highest_attendance
        - lowest_attendance
        - below_threshold_count
    """
    if not employees:
        return {
            'total_employees': 0,
            'average_attendance': 0.0,
            'highest_attendance': 0.0,
            'lowest_attendance': 0.0,
            'below_threshold_count': 0,
        }

    percentages = [e.attendance_percentage for e in employees]
    below = sum(1 for p in percentages if is_below_threshold(p))

    return {
        'total_employees': len(employees),
        'average_attendance': round(sum(percentages) / len(percentages), 2),
        'highest_attendance': round(max(percentages), 2),
        'lowest_attendance': round(min(percentages), 2),
        'below_threshold_count': below,
    }
