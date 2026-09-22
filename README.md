# Employee Attendance & Salary Processing System

A complete full-stack web application for managing employee attendance and calculating salaries, built with Python Flask, SQLite, and Bootstrap 5.

---

## Features

- **Dashboard** – Summary cards (total employees, average attendance, total salary, overtime pay, low-attendance count), 3 Chart.js charts, recent employees table, low-attendance alert table
- **Employee Management** – Add, view, edit, and delete employees with full validation
- **Live Calculation Preview** – Attendance %, overtime pay, and final salary update in real-time as you type
- **Search & Filter** – Filter employees by name, ID, department, or attendance status
- **Attendance Report** – Color-coded attendance table, below-threshold section with shortfall %
- **Salary Report** – Full salary breakdown with department filter and column totals
- **Summary Report** – Overall statistics + department-wise breakdown table
- **CSV Export** – Export attendance, salary, and summary reports as CSV files
- **Print Support** – Clean print stylesheet for all report pages
- **8 Sample Employees** – Pre-loaded on first run (3 below attendance threshold for testing)
- **Responsive UI** – Works on desktop, tablet, and mobile

---

## Technologies Used

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python 3, Flask 3.0                 |
| Database  | SQLite via SQLAlchemy ORM           |
| Frontend  | HTML5, CSS3, Bootstrap 5.3          |
| Icons     | Bootstrap Icons 1.11                |
| Charts    | Chart.js 4.4                        |
| Testing   | Python unittest                     |

---

## Project Structure

```
employee_attendance_system/
│
├── app.py                  # Application entry point
├── config.py               # Configuration (rates, threshold, DB URI)
├── requirements.txt        # Python dependencies
├── README.md
│
├── models/
│   ├── __init__.py         # SQLAlchemy db instance
│   └── employee.py         # Employee ORM model
│
├── routes/
│   ├── __init__.py
│   ├── employee_routes.py  # Dashboard + employee CRUD + API
│   └── report_routes.py    # Attendance / Salary / Summary reports + CSV
│
├── services/
│   ├── attendance_service.py   # Attendance % calculation, threshold logic
│   ├── salary_service.py       # Overtime pay, final salary, INR formatter
│   └── report_service.py       # Report builders + CSV export helpers
│
├── templates/
│   ├── base.html               # Master layout (navbar, flash messages)
│   ├── dashboard.html          # Home dashboard with charts
│   ├── employees.html          # Employee list with search/filter
│   ├── add_employee.html       # Add employee form + live preview
│   ├── edit_employee.html      # Edit employee form + live preview
│   ├── employee_details.html   # Detailed employee profile page
│   ├── attendance_report.html  # Attendance report page
│   ├── salary_report.html      # Salary report page
│   └── summary_report.html     # Summary report page
│
├── static/
│   ├── css/style.css       # Custom styles (navy theme, responsive)
│   └── js/script.js        # Global JS (validation, live search, helpers)
│
├── tests/
│   ├── __init__.py
│   └── test_calculations.py   # Unit + integration tests
│
└── instance/
    └── database.db         # SQLite database (auto-created on first run)
```

---

## Installation & Setup (Windows)

### 1. Navigate to the project folder

```cmd
cd employee_attendance_system
```

### 2. Create a virtual environment

```cmd
python -m venv venv
```

### 3. Activate the virtual environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt.

### 4. Install dependencies

```cmd
pip install -r requirements.txt
```

### 5. Run the application

```cmd
python app.py
```

On first run the application will:
1. Create `instance/database.db` automatically
2. Create the `employees` table
3. Insert 8 sample employee records (idempotent – safe to re-run)

### 6. Open in browser

```
http://127.0.0.1:5000
```

---

## Sample Data

Eight employees are pre-loaded on first run:

| Emp ID | Name          | Department | Working Days | Days Present | Attendance % | Status           |
|--------|---------------|------------|-------------|-------------|-------------|------------------|
| E001   | Rahul Sharma  | IT         | 26          | 23          | 88.46%      | Good Attendance  |
| E002   | Anil Kumar    | HR         | 26          | 19          | 73.08%      | Below Threshold  |
| E003   | Priya Patel   | Finance    | 26          | 17          | 65.38%      | Below Threshold  |
| E004   | Sneha Reddy   | Marketing  | 26          | 26          | 100.00%     | Good Attendance  |
| E005   | Arjun Singh   | IT         | 26          | 15          | 57.69%      | Below Threshold  |
| E006   | Meena Iyer    | Finance    | 26          | 24          | 92.31%      | Good Attendance  |
| E007   | Vijay Nair    | HR         | 26          | 20          | 76.92%      | Good Attendance  |
| E008   | Kavya Menon   | Marketing  | 26          | 18          | 69.23%      | Below Threshold  |

---

## Calculation Formulas

### Attendance Percentage
```
attendance_percentage = (days_present / total_working_days) × 100
```
- Rounded to 2 decimal places
- Returns 0.0 safely when total_working_days = 0

### Attendance Status
```
if attendance_percentage < 75:
    status = "Below Threshold"
else:
    status = "Good Attendance"
```
The threshold (75%) is configurable in `config.py`.

### Overtime Pay
```
overtime_pay = overtime_hours × overtime_rate
```
Default rate: **₹200 per hour** (configurable in `config.py` → `OVERTIME_RATE`)

### Final Salary
```
final_salary = basic_salary + overtime_pay
```

---

## Running Tests

```cmd
python -m pytest tests/ -v
```

Or without pytest:

```cmd
python tests/test_calculations.py
```

Tests cover:
- Attendance percentage calculation (8 cases)
- Attendance status / threshold detection (9 cases)
- Overtime pay calculation (6 cases)
- Final salary calculation (4 cases)
- Indian Rupee formatting (6 cases)
- Flask integration: create, update, delete, duplicate ID, below-threshold, all route loads

---

## Configuration

Edit `config.py` to change system-wide defaults:

```python
ATTENDANCE_THRESHOLD = 75.0    # % below which employee is flagged
OVERTIME_RATE        = 200.0   # ₹ per overtime hour
```

---

## Routes Reference

| Method | URL                          | Description                  |
|--------|------------------------------|------------------------------|
| GET    | /                            | Dashboard (home)             |
| GET    | /dashboard                   | Dashboard (alias)            |
| GET    | /employees                   | Employee list + search/filter|
| GET    | /employees/add               | Add employee form            |
| POST   | /employees/add               | Submit new employee          |
| GET    | /employees/\<pk\>            | Employee detail page         |
| GET    | /employees/\<pk\>/edit       | Edit employee form           |
| POST   | /employees/\<pk\>/edit       | Submit employee update       |
| POST   | /employees/\<pk\>/delete     | Delete employee              |
| POST   | /api/calculate               | Live calculation (JSON API)  |
| GET    | /reports/attendance          | Attendance report            |
| GET    | /reports/attendance/export   | Download attendance CSV      |
| GET    | /reports/salary              | Salary report                |
| GET    | /reports/salary/export       | Download salary CSV          |
| GET    | /reports/summary             | Summary report               |
| GET    | /reports/summary/export      | Download summary CSV         |

---

## Future Improvements

1. **Authentication** – Login/logout with role-based access (admin vs viewer)
2. **Monthly tracking** – Store attendance per month instead of a single aggregate
3. **Leave management** – Sick leave, casual leave, earned leave types
4. **PDF export** – Generate printable PDF payslips using WeasyPrint or ReportLab
5. **Email notifications** – Alert HR when employees drop below the threshold
6. **Bulk import** – Upload employees via CSV/Excel file
7. **Audit log** – Track who changed what and when
8. **REST API** – JSON API endpoints for mobile or third-party integration
9. **Multi-company** – Support multiple organisations under one deployment
10. **Dark mode** – CSS variable-based theme toggle

---

## License

This project is created for educational purposes as a student project.
