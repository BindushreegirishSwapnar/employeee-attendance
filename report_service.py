"""
Report Service
Generates attendance, salary and summary report data,
plus CSV export helpers.
"""
import csv
import io
from collections import defaultdict

from services.attendance_service import (
    get_attendance_summary,
    is_below_threshold,
)
from services.salary_service import get_salary_totals


# ── Attendance Report ────────────────────────────────────────────────────────

def build_attendance_report(employees):
    """
    Return a list of dicts suitable for rendering the attendance report table.
    Each dict contains all fields needed by the template.
    """
    report = []
    for e in employees:
        report.append({
            'employee_id':          e.employee_id,
            'name':                 e.name,
            'department':           e.department,
            'total_working_days':   e.total_working_days,
            'days_present':         e.days_present,
            'attendance_percentage': e.attendance_percentage,
            'attendance_status':    e.attendance_status,
            'is_below':             is_below_threshold(e.attendance_percentage),
        })
    return report


def build_attendance_csv(employees) -> str:
    """Return CSV string for the attendance report."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Employee ID', 'Name', 'Department',
        'Total Working Days', 'Days Present',
        'Attendance %', 'Status',
    ])
    for e in employees:
        writer.writerow([
            e.employee_id, e.name, e.department,
            e.total_working_days, e.days_present,
            e.attendance_percentage, e.attendance_status,
        ])
    return output.getvalue()


# ── Salary Report ────────────────────────────────────────────────────────────

def build_salary_report(employees):
    """Return list of dicts for the salary report table."""
    report = []
    for e in employees:
        report.append({
            'employee_id':    e.employee_id,
            'name':           e.name,
            'department':     e.department,
            'basic_salary':   e.basic_salary,
            'overtime_hours': e.overtime_hours,
            'overtime_pay':   e.overtime_pay,
            'final_salary':   e.final_salary,
        })
    return report


def build_salary_csv(employees) -> str:
    """Return CSV string for the salary report."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Employee ID', 'Name', 'Department',
        'Basic Salary (₹)', 'Overtime Hours',
        'Overtime Pay (₹)', 'Final Salary (₹)',
    ])
    for e in employees:
        writer.writerow([
            e.employee_id, e.name, e.department,
            e.basic_salary, e.overtime_hours,
            e.overtime_pay, e.final_salary,
        ])
    return output.getvalue()


# ── Summary Report ───────────────────────────────────────────────────────────

def build_summary_report(employees) -> dict:
    """
    Build a complete summary dict containing:
        - overall stats (attendance + salary)
        - department_summary list
    """
    attendance_stats = get_attendance_summary(employees)
    salary_totals = get_salary_totals(employees)

    # Department-wise aggregation
    dept_data = defaultdict(lambda: {
        'count': 0,
        'attendance_sum': 0.0,
        'salary_sum': 0.0,
    })

    for e in employees:
        d = dept_data[e.department]
        d['count'] += 1
        d['attendance_sum'] += e.attendance_percentage
        d['salary_sum'] += e.final_salary

    department_summary = []
    for dept, data in sorted(dept_data.items()):
        avg_att = round(data['attendance_sum'] / data['count'], 2) if data['count'] else 0.0
        department_summary.append({
            'department':         dept,
            'employee_count':     data['count'],
            'average_attendance': avg_att,
            'total_salary':       round(data['salary_sum'], 2),
        })

    return {
        **attendance_stats,
        **salary_totals,
        'department_summary': department_summary,
    }


def build_summary_csv(employees) -> str:
    """Return CSV string for the full summary report."""
    summary = build_summary_report(employees)
    output = io.StringIO()
    writer = csv.writer(output)

    # Overall stats
    writer.writerow(['=== OVERALL SUMMARY ==='])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Employees',        summary['total_employees']])
    writer.writerow(['Average Attendance (%)', summary['average_attendance']])
    writer.writerow(['Highest Attendance (%)', summary['highest_attendance']])
    writer.writerow(['Lowest Attendance (%)',  summary['lowest_attendance']])
    writer.writerow(['Below Threshold Count',  summary['below_threshold_count']])
    writer.writerow(['Total Basic Salary (₹)', summary['total_basic_salary']])
    writer.writerow(['Total Overtime Pay (₹)', summary['total_overtime_pay']])
    writer.writerow(['Total Final Salary (₹)', summary['total_final_salary']])
    writer.writerow([])

    # Department breakdown
    writer.writerow(['=== DEPARTMENT-WISE SUMMARY ==='])
    writer.writerow(['Department', 'Employee Count', 'Average Attendance (%)', 'Total Salary (₹)'])
    for dept in summary['department_summary']:
        writer.writerow([
            dept['department'],
            dept['employee_count'],
            dept['average_attendance'],
            dept['total_salary'],
        ])

    return output.getvalue()
