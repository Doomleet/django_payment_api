from celery import shared_task
from django.db.models import Sum
from datetime import datetime

from home.models import Home, WaterChecker, Street
from .models import PaymentProgress, Rate, FlatPayment


@shared_task
def calculate_payment_task(home_number, street_name, month, year):
    task_id = calculate_payment_task.request.id
    try:
        month = int(month)
        year = int(year)

        if not (1 <= month <= 12):
            raise ValueError("Месяц должен быть в диапазоне от 1 до 12.")

        current_year = datetime.now().year
        if not (1900 <= year <= current_year):
            raise ValueError(
                f"Год должен быть в диапазоне от 1900 до {current_year}."
                )

        if month == 1:
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        water_rate = Rate.objects.get(rate_type='water').rate
        maintenance_rate = Rate.objects.get(rate_type='maintenance').rate
    except (ValueError, Rate.DoesNotExist) as e:
        progress = PaymentProgress.objects.filter(task_id=task_id).first()
        if progress:
            progress.status = 'FAILED'
            progress.result = str(e)
            progress.save()
        return {'status': 'FAILED', 'error': str(e)}

    try:
        street = Street.objects.get(street_name=street_name)
        home = Home.objects.get(house_number=home_number, street=street)

        progress, created = PaymentProgress.objects.update_or_create(
            home=home,
            street=street,
            month=month,
            year=year,
            task_id=task_id,
            defaults={'status': 'IN_PROGRESS', 'result': None}
        )

        FlatPayment.objects.filter(payment_progress=progress).delete()

        total_calculated = 0
        flats = home.flats.all()

        for flat in flats:
            try:
                current_water = WaterChecker.objects.filter(
                    flat=flat, year=year, month=month
                ).aggregate(total=Sum('water_amount'))['total']
                previous_water = WaterChecker.objects.filter(
                    flat=flat, year=prev_year, month=prev_month
                ).aggregate(total=Sum('water_amount'))['total']

                water_consumption = current_water - previous_water
                water_cost = water_rate * water_consumption
                maintenance_cost = maintenance_rate * flat.flat_size
                total_cost = water_cost + maintenance_cost

                FlatPayment.objects.create(
                    flat=flat,
                    month=month,
                    year=year,
                    water_consumption=water_consumption,
                    water_cost=water_cost,
                    maintenance_cost=maintenance_cost,
                    total_cost=total_cost,
                    payment_progress=progress
                )

                total_calculated += total_cost

            except Exception as e:
                progress.status = 'FAILED'
                progress.result = str(e)
                progress.save()
                return f"Ошибка при расчете для квартиры {flat.id}: {e}"

        progress.result = total_calculated
        progress.status = 'COMPLETED'
        progress.save()

        return {
            'status': 'completed',
            'home_number': home_number,
            'street_name': street_name,
            'month': month,
            'year': year
        }

    except Exception as e:
        progress = PaymentProgress.objects.filter(task_id=task_id).first()
        if progress:
            progress.status = 'FAILED'
            progress.result = str(e)
            progress.save()
        return f"Ошибка при выполнении задачи: {e}"
