"""
Report Routes
Handles: attendance report, salary report, summary report + CSV exports.
"""
from flask import (
    Blueprint, render_template, request,
    Response, make_response,
)
from models.employee import Employee
from models import db
from services.report_service import (
    build_attendance_report,
    build_attendance_csv,
    build_salary_report,
    build_salary_csv,
    build_summary_report,
    build_summary_csv,
)
from services.salary_service import get_salary_totals, format_inr
from config import config

report_bp = Blueprint('report', __name__, url_prefix='/reports')


def _get_filtered_employees():
    """
    Apply optional ?department= query-param filter and return
    a list of Employee ORM objects ordered by name.
    """
    dept = request.args.get('department', '').strip()
    query = Employee.query
    if dept:
        query = query.filter(Employee.department == dept)
    return query.order_by(Employee.name).all()


def _all_departments():
    return [r[0] for r in
            db.session.query(Employee.department)
            .distinct().order_by(Employee.department).all()]


# ── Attendance Report ─────────────────────────────────────────────────────────

@report_bp.route('/attendance')
def attendance_report():
    employees = _get_filtered_employees()
    report_data = build_attendance_report(employees)
    below = [row for row in report_data if row['is_below']]

    return render_template(
        'attendance_report.html',
        report_data=report_data,
        below_threshold=below,
        departments=_all_departments(),
        dept_filter=request.args.get('department', ''),
        threshold=config.ATTENDANCE_THRESHOLD,
    )


@report_bp.route('/attendance/export')
def export_attendance_csv():
    employees = _get_filtered_employees()
    csv_data = build_attendance_csv(employees)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=attendance_report.csv'
    return response


# ── Salary Report ─────────────────────────────────────────────────────────────

@report_bp.route('/salary')
def salary_report():
    employees = _get_filtered_employees()
    report_data = build_salary_report(employees)
    totals = get_salary_totals(employees)

    return render_template(
        'salary_report.html',
        report_data=report_data,
        totals=totals,
        departments=_all_departments(),
        dept_filter=request.args.get('department', ''),
        format_inr=format_inr,
    )


@report_bp.route('/salary/export')
def export_salary_csv():
    employees = _get_filtered_employees()
    csv_data = build_salary_csv(employees)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=salary_report.csv'
    return response


# ── Summary Report ────────────────────────────────────────────────────────────

@report_bp.route('/summary')
def summary_report():
    all_employees = Employee.query.order_by(Employee.name).all()
    summary = build_summary_report(all_employees)

    return render_template(
        'summary_report.html',
        summary=summary,
        format_inr=format_inr,
        threshold=config.ATTENDANCE_THRESHOLD,
    )


@report_bp.route('/summary/export')
def export_summary_csv():
    all_employees = Employee.query.order_by(Employee.name).all()
    csv_data = build_summary_csv(all_employees)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=summary_report.csv'
    return response
