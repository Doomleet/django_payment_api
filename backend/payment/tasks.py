from celery import shared_task
from django.db.models import Sum

from home.models import Home, WaterChecker, Street
from .models import PaymentProgress, Rate


@shared_task
def calculate_payment_task(home_number, street_name, month, year):
    try:
        month = int(month)
        year = int(year)
        if month == 1:
            PREV_MONTH = -11
            prev_year = year - 1
        else:
            PREV_MONTH = 1
            prev_year = year
        water_rate = Rate.objects.get(rate_type='water').rate
        maintenance_rate = Rate.objects.get(rate_type='maintenance').rate
    except Rate.DoesNotExist:
        raise ValueError("Не найдены тарифы для расчета")

    street = Street.objects.get(street_name=street_name)
    home = Home.objects.get(house_number=home_number, street=street)
    task_id = calculate_payment_task.request.id

    progress, created = PaymentProgress.objects.update_or_create(
        home=home,
        street=street,
        month=month,
        year=year,
        task_id=task_id,
        defaults={'status': 'IN_PROGRESS', 'result': None}
    )

    total_calculated = []
    flats = home.flats.all()

    for flat in flats:
        try:
            current_water = WaterChecker.objects.filter(
                flat=flat, year=year, month=month
            ).aggregate(total=Sum('water_amount'))['total']
            previous_water = WaterChecker.objects.filter(
                flat=flat, year=prev_year, month=month-PREV_MONTH
            ).aggregate(total=Sum('water_amount'))['total']

            current_water = current_water
            previous_water = previous_water
            water_consumption = current_water - previous_water

            water_cost = water_rate * water_consumption
            maintenance_cost = maintenance_rate * flat.flat_size
            total_cost = water_cost + maintenance_cost
            total_calculated.append(f'{flat.flat_number}: {total_cost} ')

        except Exception as e:
            return f"Ошибка при расчете для квартиры {flat.id}: {e}"

    progress.result = total_calculated
    progress.status = 'COMPLETED'
    progress.save()

    return {'status': 'completed',
            'home_number': home_number,
            'street_name': street_name,
            'month': month,
            'year': year
            }
