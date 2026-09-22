"""
Employee Attendance & Salary Processing System
Entry point – run with: python app.py
"""
import os
from flask import Flask
from models import db
from config import config
from routes.employee_routes import employee_bp
from routes.report_routes import report_bp


def create_app():
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Blueprints ───────────────────────────────────────────────────────────
    app.register_blueprint(employee_bp)
    app.register_blueprint(report_bp)

    # ── Jinja2 global helpers ─────────────────────────────────────────────────
    from services.salary_service import format_inr
    app.jinja_env.globals['format_inr'] = format_inr

    return app


# ── Sample Data ───────────────────────────────────────────────────────────────

SAMPLE_EMPLOYEES = [
    {
        'employee_id':       'E001',
        'name':              'Rahul Sharma',
        'department':        'IT',
        'total_working_days': 26,
        'days_present':       23,
        'basic_salary':       30000.0,
        'overtime_hours':     10.0,
    },
    {
        'employee_id':       'E002',
        'name':              'Anil Kumar',
        'department':        'HR',
        'total_working_days': 26,
        'days_present':       19,
        'basic_salary':       25000.0,
        'overtime_hours':     5.0,
    },
    {
        'employee_id':       'E003',
        'name':              'Priya Patel',
        'department':        'Finance',
        'total_working_days': 26,
        'days_present':       17,   # Below 75 % threshold
        'basic_salary':       28000.0,
        'overtime_hours':     0.0,
    },
    {
        'employee_id':       'E004',
        'name':              'Sneha Reddy',
        'department':        'Marketing',
        'total_working_days': 26,
        'days_present':       26,
        'basic_salary':       32000.0,
        'overtime_hours':     8.0,
    },
    {
        'employee_id':       'E005',
        'name':              'Arjun Singh',
        'department':        'IT',
        'total_working_days': 26,
        'days_present':       15,   # Below 75 % threshold
        'basic_salary':       27000.0,
        'overtime_hours':     2.0,
    },
    {
        'employee_id':       'E006',
        'name':              'Meena Iyer',
        'department':        'Finance',
        'total_working_days': 26,
        'days_present':       24,
        'basic_salary':       35000.0,
        'overtime_hours':     12.0,
    },
    {
        'employee_id':       'E007',
        'name':              'Vijay Nair',
        'department':        'HR',
        'total_working_days': 26,
        'days_present':       20,
        'basic_salary':       22000.0,
        'overtime_hours':     3.0,
    },
    {
        'employee_id':       'E008',
        'name':              'Kavya Menon',
        'department':        'Marketing',
        'total_working_days': 26,
        'days_present':       18,   # Below 75 % threshold
        'basic_salary':       29000.0,
        'overtime_hours':     6.0,
    },
]


def seed_sample_data(app):
    """Insert sample employees if they don't already exist."""
    from models.employee import Employee
    from services.attendance_service import (
        calculate_attendance_percentage,
        get_attendance_status,
    )
    from services.salary_service import calculate_overtime_pay, calculate_final_salary

    with app.app_context():
        inserted = 0
        for data in SAMPLE_EMPLOYEES:
            if Employee.query.filter_by(employee_id=data['employee_id']).first():
                continue   # skip duplicates

            att_pct = calculate_attendance_percentage(
                data['days_present'], data['total_working_days']
            )
            status  = get_attendance_status(att_pct)
            ot_pay  = calculate_overtime_pay(data['overtime_hours'])
            final   = calculate_final_salary(data['basic_salary'], ot_pay)

            emp = Employee(
                employee_id          = data['employee_id'],
                name                 = data['name'],
                department           = data['department'],
                total_working_days   = data['total_working_days'],
                days_present         = data['days_present'],
                basic_salary         = data['basic_salary'],
                overtime_hours       = data['overtime_hours'],
                attendance_percentage= att_pct,
                attendance_status    = status,
                overtime_pay         = ot_pay,
                final_salary         = final,
            )
            db.session.add(emp)
            inserted += 1

        db.session.commit()
        if inserted:
            print(f'[seed] Inserted {inserted} sample employee(s).')
        else:
            print('[seed] Sample data already present – nothing inserted.')


# ── Application entry point ───────────────────────────────────────────────────

app = create_app()

if __name__ == '__main__':
    # Ensure the instance folder exists before SQLite tries to create the DB
    os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)

    with app.app_context():
        db.create_all()          # create tables if they don't exist
        seed_sample_data(app)    # insert demo data (idempotent)

    print('=' * 55)
    print('  Employee Attendance & Salary Processing System')
    print('  Running at: http://127.0.0.1:5000')
    print('  Press CTRL+C to stop.')
    print('=' * 55)

    app.run(debug=True, host='0.0.0.0', port=5000)
