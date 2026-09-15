from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta

def calculate_residual_value(on_road_price: Decimal, purchase_date: date, kilometres: int) -> dict:
    """
    Calculates the residual value and other metrics based on the given rules.
    """
    on_road_price = Decimal(on_road_price)
    kilometres = Decimal(kilometres)

    assumed_depreciation = on_road_price * Decimal('0.70')
    ltk = Decimal('200000')
    ltm = Decimal('150')

    akm = assumed_depreciation / ltk
    adm = assumed_depreciation / ltm

    today = date.today()
    delta = relativedelta(today, purchase_date)
    actual_months_used = Decimal(delta.years * 12 + delta.months)
    
    # Handle future purchase dates gracefully
    if actual_months_used < 0:
        actual_months_used = Decimal(0)

    dcm = actual_months_used * adm
    dck = kilometres * akm

    total_depreciation = dcm + dck
    
    # Ensure depreciation does not exceed on_road_price
    if total_depreciation >= on_road_price:
        residual_value = Decimal('0')
    else:
        residual_value = on_road_price - total_depreciation

    # Round to nearest 1000
    # Add 500 effectively rounds to nearest 1000 properly with quantize or just standard math
    rounded_residual_value = (residual_value / Decimal('1000')).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * Decimal('1000')

    # Final Price (-5%)
    final_price = rounded_residual_value * Decimal('0.95')

    return {
        'assumed_depreciation': assumed_depreciation.quantize(Decimal('0.01')),
        'actual_months_used': int(actual_months_used),
        'total_depreciation': total_depreciation.quantize(Decimal('0.01')),
        'residual_value': residual_value.quantize(Decimal('0.01')),
        'rounded_residual_value': rounded_residual_value.quantize(Decimal('0.01')),
        'final_price': final_price.quantize(Decimal('0.01')),
    }
