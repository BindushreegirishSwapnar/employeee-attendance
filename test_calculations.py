"""
Unit Tests – Employee Attendance & Salary Processing System
Run with:  python -m pytest tests/ -v
       or: python tests/test_calculations.py
"""
import sys
import os
import unittest

# Allow imports from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.attendance_service import (
    calculate_attendance_percentage,
    get_attendance_status,
    is_below_threshold,
)
from services.salary_service import (
    calculate_overtime_pay,
    calculate_final_salary,
    calculate_all,
    format_inr,
)


# ══════════════════════════════════════════════════════════════
# Attendance Calculation Tests
# ══════════════════════════════════════════════════════════════

class TestAttendanceCalculation(unittest.TestCase):
    """Tests for calculate_attendance_percentage()"""

    def test_normal_attendance(self):
        """Working Days=26, Present=23 → 88.46%"""
        result = calculate_attendance_percentage(23, 26)
        self.assertEqual(result, 88.46)

    def test_full_attendance(self):
        """100 % attendance when present == working days"""
        result = calculate_attendance_percentage(26, 26)
        self.assertEqual(result, 100.0)

    def test_zero_attendance(self):
        """0 % when no days present"""
        result = calculate_attendance_percentage(0, 26)
        self.assertEqual(result, 0.0)

    def test_below_threshold_attendance(self):
        """Working Days=26, Present=17 → 65.38%"""
        result = calculate_attendance_percentage(17, 26)
        self.assertEqual(result, 65.38)

    def test_low_attendance_second_case(self):
        """Working Days=26, Present=15 → 57.69%"""
        result = calculate_attendance_percentage(15, 26)
        self.assertEqual(result, 57.69)

    def test_division_by_zero(self):
        """Should return 0.0 when total_working_days=0 (no crash)"""
        result = calculate_attendance_percentage(5, 0)
        self.assertEqual(result, 0.0)

    def test_rounding(self):
        """Result must be rounded to 2 decimal places"""
        result = calculate_attendance_percentage(1, 3)   # 33.333…%
        self.assertEqual(result, 33.33)

    def test_partial_attendance(self):
        """Working Days=30, Present=22 → 73.33%"""
        result = calculate_attendance_percentage(22, 30)
        self.assertEqual(result, 73.33)


# ══════════════════════════════════════════════════════════════
# Attendance Status / Threshold Tests
# ══════════════════════════════════════════════════════════════

class TestAttendanceStatus(unittest.TestCase):
    """Tests for get_attendance_status() and is_below_threshold()"""

    def test_good_attendance_at_threshold(self):
        """Exactly 75 % is 'Good Attendance' (not below)"""
        self.assertEqual(get_attendance_status(75.0), 'Good Attendance')

    def test_good_attendance_above_threshold(self):
        self.assertEqual(get_attendance_status(88.46), 'Good Attendance')

    def test_good_attendance_100_percent(self):
        self.assertEqual(get_attendance_status(100.0), 'Good Attendance')

    def test_below_threshold_just_under(self):
        """74.99 % is 'Below Threshold'"""
        self.assertEqual(get_attendance_status(74.99), 'Below Threshold')

    def test_below_threshold_65_percent(self):
        """65.38 % → Below Threshold"""
        self.assertEqual(get_attendance_status(65.38), 'Below Threshold')

    def test_below_threshold_zero(self):
        """0 % is always Below Threshold"""
        self.assertEqual(get_attendance_status(0.0), 'Below Threshold')

    def test_is_below_threshold_true(self):
        self.assertTrue(is_below_threshold(65.38))

    def test_is_below_threshold_false(self):
        self.assertFalse(is_below_threshold(88.46))

    def test_is_below_threshold_exactly_at(self):
        """75.0 % is NOT below threshold"""
        self.assertFalse(is_below_threshold(75.0))


# ══════════════════════════════════════════════════════════════
# Overtime Pay Tests
# ══════════════════════════════════════════════════════════════

class TestOvertimeCalculation(unittest.TestCase):
    """Tests for calculate_overtime_pay()"""

    def test_standard_overtime(self):
        """10 hrs × ₹200 = ₹2,000"""
        result = calculate_overtime_pay(10, overtime_rate=200)
        self.assertEqual(result, 2000.0)

    def test_zero_overtime(self):
        """0 hrs → ₹0"""
        result = calculate_overtime_pay(0, overtime_rate=200)
        self.assertEqual(result, 0.0)

    def test_fractional_overtime(self):
        """5.5 hrs × ₹200 = ₹1,100"""
        result = calculate_overtime_pay(5.5, overtime_rate=200)
        self.assertEqual(result, 1100.0)

    def test_custom_rate(self):
        """10 hrs × ₹250 = ₹2,500"""
        result = calculate_overtime_pay(10, overtime_rate=250)
        self.assertEqual(result, 2500.0)

    def test_negative_hours_treated_as_zero(self):
        """Negative overtime hours should be clamped to 0"""
        result = calculate_overtime_pay(-5, overtime_rate=200)
        self.assertEqual(result, 0.0)

    def test_default_rate_used(self):
        """When no rate supplied, default config rate (200) is used"""
        result = calculate_overtime_pay(10)   # uses config.OVERTIME_RATE = 200
        self.assertEqual(result, 2000.0)


# ══════════════════════════════════════════════════════════════
# Final Salary Tests
# ══════════════════════════════════════════════════════════════

class TestFinalSalaryCalculation(unittest.TestCase):
    """Tests for calculate_final_salary()"""

    def test_standard_final_salary(self):
        """Basic=30,000 + OT Pay=2,000 → Final=32,000"""
        result = calculate_final_salary(30000.0, 2000.0)
        self.assertEqual(result, 32000.0)

    def test_zero_overtime_pay(self):
        """Basic=25,000 + OT Pay=0 → Final=25,000"""
        result = calculate_final_salary(25000.0, 0.0)
        self.assertEqual(result, 25000.0)

    def test_large_salary(self):
        """Basic=1,00,000 + OT=5,000 → 1,05,000"""
        result = calculate_final_salary(100000.0, 5000.0)
        self.assertEqual(result, 105000.0)

    def test_calculate_all_convenience(self):
        """calculate_all() must return correct overtime_pay and final_salary"""
        result = calculate_all(30000.0, 10.0, overtime_rate=200)
        self.assertEqual(result['overtime_pay'], 2000.0)
        self.assertEqual(result['final_salary'], 32000.0)


# ══════════════════════════════════════════════════════════════
# format_inr Tests
# ══════════════════════════════════════════════════════════════

class TestFormatINR(unittest.TestCase):
    """Tests for format_inr() Indian Rupee formatter"""

    def test_thousands(self):
        self.assertEqual(format_inr(1000), '₹1,000.00')

    def test_lakhs(self):
        self.assertEqual(format_inr(100000), '₹1,00,000.00')

    def test_crore(self):
        self.assertEqual(format_inr(10000000), '₹1,00,00,000.00')

    def test_zero(self):
        self.assertEqual(format_inr(0), '₹0.00')

    def test_with_decimal(self):
        self.assertEqual(format_inr(32000.50), '₹32,000.50')

    def test_small_amount(self):
        self.assertEqual(format_inr(500), '₹500.00')


# ══════════════════════════════════════════════════════════════
# Flask App / Database Integration Tests
# ══════════════════════════════════════════════════════════════

class TestFlaskApp(unittest.TestCase):
    """Integration tests: employee CRUD via Flask test client."""

    def setUp(self):
        """Set up an in-memory SQLite test app."""
        import app as app_module
        from models import db as _db

        self.app_module = app_module
        self._db = _db

        test_app = app_module.create_app()
        test_app.config['TESTING']                  = True
        test_app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///:memory:'
        test_app.config['WTF_CSRF_ENABLED']         = False

        self.app    = test_app
        self.client = test_app.test_client()

        with test_app.app_context():
            _db.create_all()

    def tearDown(self):
        with self.app.app_context():
            self._db.session.remove()
            self._db.drop_all()

    # ── Helpers ──────────────────────────────────────────────

    def _post_add(self, data):
        return self.client.post(
            '/employees/add',
            data=data,
            follow_redirects=True
        )

    def _sample_data(self, emp_id='T001'):
        return {
            'employee_id':       emp_id,
            'name':              'Test User',
            'department':        'IT',
            'total_working_days': '26',
            'days_present':       '23',
            'basic_salary':       '30000',
            'overtime_hours':     '10',
        }

    # ── Employee Creation ─────────────────────────────────────

    def test_create_employee(self):
        """POST to /employees/add creates a new employee record."""
        from models.employee import Employee
        resp = self._post_add(self._sample_data())
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            emp = Employee.query.filter_by(employee_id='T001').first()
            self.assertIsNotNone(emp)
            self.assertEqual(emp.name, 'Test User')

    def test_calculated_fields_on_create(self):
        """Calculations are stored correctly when employee is created."""
        from models.employee import Employee
        self._post_add(self._sample_data())

        with self.app.app_context():
            emp = Employee.query.filter_by(employee_id='T001').first()
            self.assertEqual(emp.attendance_percentage, 88.46)
            self.assertEqual(emp.overtime_pay,          2000.0)
            self.assertEqual(emp.final_salary,          32000.0)
            self.assertEqual(emp.attendance_status,     'Good Attendance')

    # ── Duplicate Employee ID ─────────────────────────────────

    def test_duplicate_employee_id_rejected(self):
        """Submitting the same employee_id twice shows an error flash."""
        self._post_add(self._sample_data('T002'))
        resp = self._post_add(self._sample_data('T002'))
        self.assertIn(b'already exists', resp.data)

        from models.employee import Employee
        with self.app.app_context():
            count = Employee.query.filter_by(employee_id='T002').count()
            self.assertEqual(count, 1)

    # ── Employee Update ───────────────────────────────────────

    def test_update_employee(self):
        """PUT-style POST to /employees/<pk>/edit updates the record."""
        from models.employee import Employee
        self._post_add(self._sample_data('T003'))

        with self.app.app_context():
            emp = Employee.query.filter_by(employee_id='T003').first()
            emp_pk = emp.id

        updated = {
            'name':              'Updated Name',
            'department':        'HR',
            'total_working_days': '26',
            'days_present':       '20',
            'basic_salary':       '35000',
            'overtime_hours':     '5',
        }
        resp = self.client.post(
            f'/employees/{emp_pk}/edit',
            data=updated,
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            emp = Employee.query.get(emp_pk)
            self.assertEqual(emp.name,       'Updated Name')
            self.assertEqual(emp.department, 'HR')
            self.assertEqual(emp.attendance_percentage,
                             calculate_attendance_percentage(20, 26))

    # ── Employee Deletion ─────────────────────────────────────

    def test_delete_employee(self):
        """POST to /employees/<pk>/delete removes the record."""
        from models.employee import Employee
        self._post_add(self._sample_data('T004'))

        with self.app.app_context():
            emp_pk = Employee.query.filter_by(employee_id='T004').first().id

        resp = self.client.post(
            f'/employees/{emp_pk}/delete',
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)

        with self.app.app_context():
            emp = Employee.query.get(emp_pk)
            self.assertIsNone(emp)

    # ── Below-threshold employee ──────────────────────────────

    def test_below_threshold_employee_status(self):
        """Employee with 65.38 % attendance is flagged Below Threshold."""
        from models.employee import Employee
        data = self._sample_data('T005')
        data['days_present'] = '17'   # 17/26 = 65.38 %
        self._post_add(data)

        with self.app.app_context():
            emp = Employee.query.filter_by(employee_id='T005').first()
            self.assertEqual(emp.attendance_percentage, 65.38)
            self.assertEqual(emp.attendance_status,     'Below Threshold')

    # ── Dashboard route ───────────────────────────────────────

    def test_dashboard_loads(self):
        """GET / returns HTTP 200."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    # ── Employee list route ───────────────────────────────────

    def test_employees_list_loads(self):
        """GET /employees returns HTTP 200."""
        resp = self.client.get('/employees')
        self.assertEqual(resp.status_code, 200)

    # ── Reports load ──────────────────────────────────────────

    def test_attendance_report_loads(self):
        resp = self.client.get('/reports/attendance')
        self.assertEqual(resp.status_code, 200)

    def test_salary_report_loads(self):
        resp = self.client.get('/reports/salary')
        self.assertEqual(resp.status_code, 200)

    def test_summary_report_loads(self):
        resp = self.client.get('/reports/summary')
        self.assertEqual(resp.status_code, 200)


# ── Entry point ───────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)
