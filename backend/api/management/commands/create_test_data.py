from django.core.management.base import BaseCommand
from home.models import Home, WaterChecker, Flat, Street
from payment.models import Rate
import random

START_HOME_NUM = 1
END_HOME_NUM = 4
HOME_1_FLATS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
HOME_2_FLATS = [x + 10 for x in HOME_1_FLATS]
HOME_3_FLATS = [x + 20 for x in HOME_1_FLATS]


class Command(BaseCommand):
    def handle(self, *args, **options):
        rates = [
            {'rate_type': 'water', 'rate': 3},
            {'rate_type': 'maintenance', 'rate': 5},
        ]
        for rate_data in rates:
            Rate.objects.create(**rate_data)
        street1 = Street.objects.create(street_name='Первая улица')
        street2 = Street.objects.create(street_name='Вторая улица')
        homes = []
        for home_number in range(START_HOME_NUM, END_HOME_NUM):
            if home_number == 1:
                flats = HOME_1_FLATS
                street = street1
            elif home_number == 2:
                flats = HOME_2_FLATS
                street = street2
            else:
                flats = HOME_3_FLATS
                street = street1
            home = Home.objects.create(
                house_number=home_number,
                street=street
            )
            homes.append(home)
            for flat_number in flats:
                flat = Flat.objects.create(
                    flat_number=flat_number,
                    flat_size=round(random.uniform(30.0, 100.0), 1)
                )
                home.flats.add(flat)

        for home in homes:
            flats = home.flats.all()
            for flat in flats:
                num_checkers = random.randint(1, 3)
                for _ in range(num_checkers):
                    prev_water_amount = 0
                    for year in range(2022, 2024):
                        for month in range(1, 13):
                            if month == 1 and year == 2022:
                                current_water_amount = round(random.uniform(100.0, 1000.0), 1)
                            else:
                                current_water_amount = prev_water_amount + round(random.uniform(100.0, 1000.0), 1)

                            WaterChecker.objects.create(
                                home=home,
                                flat=flat,
                                year=year,
                                month=month,
                                water_amount=current_water_amount
                            )

                            prev_water_amount = current_water_amount

        self.stdout.write(self.style.SUCCESS('БД заполнена.'))
