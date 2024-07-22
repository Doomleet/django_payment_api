from django.db import models


class Street(models.Model):
    street_name = models.CharField(max_length=255)

    def __str__(self):
        return self.street_name


class WaterChecker(models.Model):
    home = models.ForeignKey(
        'Home',
        related_name='water_checkers',
        on_delete=models.CASCADE,
        verbose_name='Дом'
    )
    flat = models.ForeignKey(
        'Flat',
        related_name='water_checkers',
        on_delete=models.CASCADE,
        verbose_name='Квартира'
    )
    year = models.PositiveIntegerField(verbose_name='Год')
    month = models.PositiveIntegerField(verbose_name='Месяц',
                                        choices=[(i, i) for i in range(1, 13)]
                                        )
    water_amount = models.FloatField(verbose_name='Количество воды')

    def __str__(self):
        return f'{self.home}-{self.flat}-{self.year}-{self.month}'


class Flat(models.Model):
    flat_number = models.IntegerField()
    flat_size = models.FloatField()

    def __str__(self):
        return f'{self.flat_number}'


class Home(models.Model):
    house_number = models.IntegerField()
    street = models.ForeignKey(
        Street,
        related_name='homes',
        on_delete=models.CASCADE,
        verbose_name='Название улицы',
        null=True,
        blank=True
    )
    flats = models.ManyToManyField(
        Flat,
        related_name='flates',
        blank=True
    )

    class Meta:
        unique_together = ('house_number', 'street')

    def __str__(self):
        return f'{self.house_number}'
