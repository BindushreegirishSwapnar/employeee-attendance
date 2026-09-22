import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'employee-attendance-secret-key-2024')

    # SQLite database stored in the instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'database.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Attendance ──────────────────────────────────────────────────────────────
    ATTENDANCE_THRESHOLD = 75.0          # percent; below this → "Below Threshold"

    # ── Overtime ────────────────────────────────────────────────────────────────
    OVERTIME_RATE = 200.0                # ₹ per overtime hour (change here only)

    # ── Pagination ──────────────────────────────────────────────────────────────
    EMPLOYEES_PER_PAGE = 10


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Default to development
config = DevelopmentConfig()
