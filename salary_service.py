"""
Salary Service
Handles overtime and final salary calculations.
"""
from config import config


def calculate_overtime_pay(overtime_hours: float, overtime_rate: float = None) -> float:
    """
    Calculate overtime pay.

    Formula: overtime_hours * overtime_rate
    Uses the configured default rate when no rate is supplied.
    """
    if overtime_rate is None:
        overtime_rate = config.OVERTIME_RATE
    if overtime_hours < 0:
        overtime_hours = 0.0
    return round(overtime_hours * overtime_rate, 2)


def calculate_final_salary(basic_salary: float, overtime_pay: float) -> float:
    """
    Calculate final (gross) salary.

    Formula: basic_salary + overtime_pay
    """
    return round(basic_salary + overtime_pay, 2)


def calculate_all(basic_salary: float, overtime_hours: float,
                  overtime_rate: float = None) -> dict:
    """
    Convenience function – compute overtime_pay and final_salary in one call.

    Returns:
        {
            'overtime_pay':  <float>,
            'final_salary':  <float>,
        }
    """
    overtime_pay = calculate_overtime_pay(overtime_hours, overtime_rate)
    final_salary = calculate_final_salary(basic_salary, overtime_pay)
    return {
        'overtime_pay': overtime_pay,
        'final_salary': final_salary,
    }


def get_salary_totals(employees) -> dict:
    """
    Given a list of Employee ORM objects, return aggregated salary totals.

    Returns:
        {
            'total_basic_salary':   <float>,
            'total_overtime_pay':   <float>,
            'total_final_salary':   <float>,
        }
    """
    total_basic = sum(e.basic_salary for e in employees)
    total_overtime = sum(e.overtime_pay for e in employees)
    total_final = sum(e.final_salary for e in employees)

    return {
        'total_basic_salary': round(total_basic, 2),
        'total_overtime_pay': round(total_overtime, 2),
        'total_final_salary': round(total_final, 2),
    }


def format_inr(amount: float) -> str:
    """
    Format a number as Indian Rupee string with comma separators.
    Example: 1234567.5 → '₹12,34,567.50'
    """
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return '₹0.00'

    # Split integer and decimal parts
    is_negative = amount < 0
    amount = abs(amount)
    paise = f'{amount:.2f}'.split('.')[1]
    integer_part = int(amount)

    # Indian number system: last 3 digits, then groups of 2
    s = str(integer_part)
    if len(s) <= 3:
        result = s
    else:
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + ',' + result
            s = s[:-2]

    formatted = f'₹{result}.{paise}'
    if is_negative:
        formatted = '-' + formatted
    return formatted
