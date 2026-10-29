from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from config import DISCOUNT_PERCENT
from database.product_repository import get_ordered_product_ids


def get_previous_month_range(calculation_date):
    """Возвращает [начало предыдущего месяца; начало текущего месяца)."""
    current_month_start = calculation_date.replace(day=1)
    if current_month_start.month == 1:
        previous_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
    else:
        previous_month_start = current_month_start.replace(month=current_month_start.month - 1)
    return previous_month_start, current_month_start


def calculate_final_price(price, has_orders_last_month):
    price = Decimal(price)
    if has_orders_last_month:
        return price
    multiplier = Decimal(100 - DISCOUNT_PERCENT) / Decimal(100)
    return (price * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def apply_discounts(products, calculation_date=None):
    """Скидка 25% на товары, которые не заказывали за предыдущий календарный месяц."""
    if calculation_date is None:
        calculation_date = date.today()
    period_start, period_end = get_previous_month_range(calculation_date)
    ordered_ids = get_ordered_product_ids(period_start, period_end)
    for product in products:
        has_orders = product["product_id"] in ordered_ids
        product["final_price"] = calculate_final_price(product["price"], has_orders)
        product["has_discount"] = not has_orders
    return products


def format_price(value):
    return f"{Decimal(value):,.2f} ₽".replace(",", " ")


def format_size(size_value):
    return f"{Decimal(size_value).normalize():f}"