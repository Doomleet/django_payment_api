from django.db import models

from home.models import Home, Street, Flat


class BaseModel(models.Model):
    month = models.PositiveIntegerField(verbose_name='Месяц',
                                        choices=[(i, i) for i in range(1, 13)])
    year = models.PositiveIntegerField(verbose_name='Год')

    class Meta:
        abstract = True


class Rate(models.Model):
    RATE_CHOICES = [
        ('water', 'Водоснабжение'),
        ('maintenance', 'Содержание общего имущества'),
    ]
    rate_type = models.CharField(max_length=20,
                                 choices=RATE_CHOICES,
                                 unique=True)
    rate = models.FloatField()

    def __str__(self):
        return f'{self.get_rate_type_display()}: {self.rate}'


class PaymentProgress(BaseModel):
    STATUS_CHOICES = [
        ('PENDING', 'В ожидании'),
        ('IN_PROGRESS', 'В процессе'),
        ('COMPLETED', 'Завершено'),
        ('FAILED', 'Ошибка')
    ]

    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    street = models.ForeignKey(Street, on_delete=models.CASCADE)
    result = models.CharField(null=True, blank=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='PENDING'
                              )
    task_id = models.CharField(max_length=255,
                               unique=True,
                               null=True,
                               blank=True)

    def __str__(self):
        return f'{self.home}-{self.street}-{self.month}/{self.year}:{self.status}'


class FlatPayment(BaseModel):
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    water_consumption = models.FloatField()
    water_cost = models.FloatField()
    maintenance_cost = models.FloatField()
    total_cost = models.FloatField()
    payment_progress = models.ForeignKey(PaymentProgress,
                                         on_delete=models.CASCADE,
                                         related_name='flat_payments'
                                         )

    def __str__(self):
        return f'Квартира {self.flat.flat_number} - {self.total_cost}'
