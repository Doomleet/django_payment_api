from django.db import models
from home.models import Home, Street


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


class PaymentProgress(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'В ожидании'),
        ('IN_PROGRESS', 'В процессе'),
        ('COMPLETED', 'Завершено')
    ]

    home = models.ForeignKey(Home, on_delete=models.CASCADE)
    street = models.ForeignKey(Street, on_delete=models.CASCADE)
    month = models.PositiveIntegerField(verbose_name='Месяц',
                                        choices=[(i, i) for i in range(1, 13)])
    year = models.PositiveIntegerField(verbose_name='Год')
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
