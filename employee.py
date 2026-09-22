from datetime import datetime
from models import db


class Employee(db.Model):
    """SQLAlchemy model representing a single employee record."""

    __tablename__ = 'employees'

    # ── Primary key ─────────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Identification ──────────────────────────────────────────────────────────
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    # ── Attendance raw data ──────────────────────────────────────────────────────
    total_working_days = db.Column(db.Integer, nullable=False, default=0)
    days_present = db.Column(db.Integer, nullable=False, default=0)

    # ── Salary raw data ──────────────────────────────────────────────────────────
    basic_salary = db.Column(db.Float, nullable=False, default=0.0)
    overtime_hours = db.Column(db.Float, nullable=False, default=0.0)

    # ── Computed / stored values ─────────────────────────────────────────────────
    attendance_percentage = db.Column(db.Float, nullable=False, default=0.0)
    overtime_pay = db.Column(db.Float, nullable=False, default=0.0)
    final_salary = db.Column(db.Float, nullable=False, default=0.0)
    attendance_status = db.Column(db.String(30), nullable=False, default='Good Attendance')

    # ── Metadata ─────────────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # ────────────────────────────────────────────────────────────────────────────

    def __repr__(self):
        return f'<Employee {self.employee_id} – {self.name}>'

    def to_dict(self):
        """Return a plain dict representation (useful for JSON / CSV export)."""
        return {
            'employee_id':          self.employee_id,
            'name':                 self.name,
            'department':           self.department,
            'total_working_days':   self.total_working_days,
            'days_present':         self.days_present,
            'basic_salary':         self.basic_salary,
            'overtime_hours':       self.overtime_hours,
            'attendance_percentage': self.attendance_percentage,
            'overtime_pay':         self.overtime_pay,
            'final_salary':         self.final_salary,
            'attendance_status':    self.attendance_status,
            'created_at':           self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
