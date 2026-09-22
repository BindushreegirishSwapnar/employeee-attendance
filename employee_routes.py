"""
Employee Routes
Handles: list, add, view, edit, delete employees + dashboard.
"""
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify,
)
from models import db
from models.employee import Employee
from services.attendance_service import (
    calculate_attendance_percentage,
    get_attendance_status,
    get_attendance_summary,
)
from services.salary_service import (
    calculate_overtime_pay,
    calculate_final_salary,
    get_salary_totals,
    format_inr,
)
from config import config
from collections import defaultdict

employee_bp = Blueprint('employee', __name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _recalculate_and_update(employee, form_data: dict):
    """Apply form data to an Employee object and recompute derived fields."""
    employee.name = form_data['name'].strip()
    employee.department = form_data['department'].strip()
    employee.total_working_days = int(form_data['total_working_days'])
    employee.days_present = int(form_data['days_present'])
    employee.basic_salary = float(form_data['basic_salary'])
    employee.overtime_hours = float(form_data['overtime_hours'])

    employee.attendance_percentage = calculate_attendance_percentage(
        employee.days_present, employee.total_working_days
    )
    employee.attendance_status = get_attendance_status(employee.attendance_percentage)
    employee.overtime_pay = calculate_overtime_pay(employee.overtime_hours)
    employee.final_salary = calculate_final_salary(employee.basic_salary, employee.overtime_pay)


def _validate_form(form, is_new=True, existing_id=None):
    """Validate employee form data. Returns list of error strings."""
    errors = []

    if is_new:
        emp_id = form.get('employee_id', '').strip()
        if not emp_id:
            errors.append('Employee ID is required.')
        elif Employee.query.filter_by(employee_id=emp_id).first():
            errors.append(f'Employee ID "{emp_id}" already exists.')

    name = form.get('name', '').strip()
    if not name:
        errors.append('Employee Name is required.')

    dept = form.get('department', '').strip()
    if not dept:
        errors.append('Department is required.')

    try:
        total_days = int(form.get('total_working_days', 0))
        if total_days <= 0:
            errors.append('Total Working Days must be greater than 0.')
    except (ValueError, TypeError):
        errors.append('Total Working Days must be a valid number.')
        total_days = 0

    try:
        days_present = int(form.get('days_present', 0))
        if days_present < 0:
            errors.append('Days Present cannot be negative.')
        elif total_days > 0 and days_present > total_days:
            errors.append('Days Present cannot exceed Total Working Days.')
    except (ValueError, TypeError):
        errors.append('Days Present must be a valid number.')

    try:
        basic_salary = float(form.get('basic_salary', 0))
        if basic_salary < 0:
            errors.append('Basic Salary cannot be negative.')
    except (ValueError, TypeError):
        errors.append('Basic Salary must be a valid number.')

    try:
        ot_hours = float(form.get('overtime_hours', 0))
        if ot_hours < 0:
            errors.append('Overtime Hours cannot be negative.')
    except (ValueError, TypeError):
        errors.append('Overtime Hours must be a valid number.')

    return errors


# ── Dashboard ────────────────────────────────────────────────────────────────

@employee_bp.route('/')
@employee_bp.route('/dashboard')
def dashboard():
    all_employees = Employee.query.order_by(Employee.created_at.desc()).all()

    # Summary cards
    attendance_stats = get_attendance_summary(all_employees)
    salary_totals = get_salary_totals(all_employees)

    # Recent 5 employees
    recent_employees = all_employees[:5]

    # Below-threshold employees
    below_threshold = [e for e in all_employees
                       if e.attendance_status == 'Below Threshold']

    # Department-wise count for chart
    dept_count = defaultdict(int)
    dept_salary = defaultdict(float)
    status_count = {'Good Attendance': 0, 'Below Threshold': 0}
    for e in all_employees:
        dept_count[e.department] += 1
        dept_salary[e.department] += e.final_salary
        status_count[e.attendance_status] += 1

    dept_labels = list(dept_count.keys())
    dept_counts = [dept_count[d] for d in dept_labels]
    dept_salaries = [dept_salary[d] for d in dept_labels]

    return render_template(
        'dashboard.html',
        stats={**attendance_stats, **salary_totals},
        recent_employees=recent_employees,
        below_threshold=below_threshold,
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        dept_salaries=dept_salaries,
        status_labels=list(status_count.keys()),
        status_counts=list(status_count.values()),
        format_inr=format_inr,
        config=config,
    )


# ── Employee List ─────────────────────────────────────────────────────────────

@employee_bp.route('/employees')
def employees():
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('department', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Employee.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Employee.employee_id.ilike(like),
                Employee.name.ilike(like),
            )
        )

    if dept_filter:
        query = query.filter(Employee.department == dept_filter)

    if status_filter:
        query = query.filter(Employee.attendance_status == status_filter)

    all_employees = query.order_by(Employee.name).all()

    # Unique departments for filter dropdown
    departments = [r[0] for r in db.session.query(Employee.department).distinct().order_by(Employee.department).all()]

    return render_template(
        'employees.html',
        employees=all_employees,
        departments=departments,
        search=search,
        dept_filter=dept_filter,
        status_filter=status_filter,
        format_inr=format_inr,
    )


# ── Add Employee ─────────────────────────────────────────────────────────────

@employee_bp.route('/employees/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        errors = _validate_form(request.form, is_new=True)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('add_employee.html',
                                   form_data=request.form,
                                   config=config)

        try:
            employee = Employee(employee_id=request.form['employee_id'].strip())
            _recalculate_and_update(employee, request.form)
            db.session.add(employee)
            db.session.commit()
            flash(f'Employee {employee.name} added successfully.', 'success')
            return redirect(url_for('employee.employees'))
        except Exception as exc:
            db.session.rollback()
            flash(f'Database error: {exc}', 'danger')

    return render_template('add_employee.html', form_data={}, config=config)


# ── View Employee ─────────────────────────────────────────────────────────────

@employee_bp.route('/employees/<int:emp_pk>')
def employee_detail(emp_pk):
    employee = db.session.get(Employee, emp_pk)
    if not employee:
        from flask import abort
        abort(404)
    return render_template('employee_details.html',
                           employee=employee,
                           format_inr=format_inr,
                           config=config)


# ── Edit Employee ─────────────────────────────────────────────────────────────

@employee_bp.route('/employees/<int:emp_pk>/edit', methods=['GET', 'POST'])
def edit_employee(emp_pk):
    employee = db.session.get(Employee, emp_pk)
    if not employee:
        from flask import abort
        abort(404)

    if request.method == 'POST':
        errors = _validate_form(request.form, is_new=False)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('edit_employee.html',
                                   employee=employee,
                                   form_data=request.form,
                                   config=config)

        try:
            _recalculate_and_update(employee, request.form)
            db.session.commit()
            flash(f'Employee {employee.name} updated successfully.', 'success')
            return redirect(url_for('employee.employee_detail', emp_pk=employee.id))
        except Exception as exc:
            db.session.rollback()
            flash(f'Database error: {exc}', 'danger')

    return render_template('edit_employee.html',
                           employee=employee,
                           form_data={},
                           config=config)


# ── Delete Employee ───────────────────────────────────────────────────────────

@employee_bp.route('/employees/<int:emp_pk>/delete', methods=['POST'])
def delete_employee(emp_pk):
    employee = Employee.query.get_or_404(emp_pk)
    name = employee.name
    try:
        db.session.delete(employee)
        db.session.commit()
        flash(f'Employee {name} deleted successfully.', 'success')
    except Exception as exc:
        db.session.rollback()
        flash(f'Database error: {exc}', 'danger')
    return redirect(url_for('employee.employees'))


# ── AJAX: Live Calculation ────────────────────────────────────────────────────

@employee_bp.route('/api/calculate', methods=['POST'])
def api_calculate():
    """Return computed values as JSON for the live preview in the form."""
    try:
        data = request.get_json(force=True)
        total_days = float(data.get('total_working_days', 0) or 0)
        days_present = float(data.get('days_present', 0) or 0)
        basic_salary = float(data.get('basic_salary', 0) or 0)
        overtime_hours = float(data.get('overtime_hours', 0) or 0)

        att_pct = calculate_attendance_percentage(days_present, total_days)
        status = get_attendance_status(att_pct)
        ot_pay = calculate_overtime_pay(overtime_hours)
        final = calculate_final_salary(basic_salary, ot_pay)

        return jsonify({
            'attendance_percentage': att_pct,
            'attendance_status': status,
            'overtime_pay': ot_pay,
            'final_salary': final,
            'overtime_rate': config.OVERTIME_RATE,
        })
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400
