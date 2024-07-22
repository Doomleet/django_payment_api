from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from home.models import Home, Street
from .models import PaymentProgress
from .serializers import PaymentProgressSerializer
from .tasks import calculate_payment_task
from django.shortcuts import get_object_or_404


class PaymentCalculationView(APIView):
    '''

    POST:
    Запускает задачу расчёта квартплаты и сохраняет прогресс выполнения задачи.

    Параметры:
    home_number (int): Номер дома.
    street_name (str): Название улицы.
    month (int): Месяц расчёта.
    year (int): Год расчёта.

    Возвращает:
    task_id (str): ID запущенной задачи.

    '''
    def post(self, request):
        home_number = request.data.get('home_number')
        street_name = request.data.get('street_name')
        month = request.data.get('month')
        year = request.data.get('year')

        if not all([home_number, street_name, month, year]):
            return Response({'error':
                             'Параметры: home_number,street_name,month,year'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            home = Home.objects.get(house_number=home_number)
            street = Street.objects.get(street_name=street_name)
        except Home.DoesNotExist:
            return Response({'error': f'Дом {home_number} не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Street.DoesNotExist:
            return Response({'error': f'Улица {street_name} не найдена'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

        task = calculate_payment_task.delay(
            home_number,
            street_name,
            month,
            year
        )
        progress, created = PaymentProgress.objects.get_or_create(
            home=home,
            street=street,
            month=int(month),
            year=int(year),
            task_id=task.id,
            defaults={'status': 'PENDING'}
        )

        if not created:
            progress.status = 'PENDING'
            progress.task_id = task.id
            progress.save()

        return Response({'task_id': task.id}, status=status.HTTP_201_CREATED)


class PaymentProgressView(APIView):
    '''

    Получаем статус выполнения задачи расчёта квартплаты по ID задачи.

    GET:
    Возвращает статус выполнения и результат задачи расчёта квартплаты.

    Параметры:
    task_id (str): ID задачи.

    Возвращает:
    Статус выполнения и результат задачи.

    '''
    def get(self, request, task_id):
        progress = get_object_or_404(PaymentProgress, task_id=task_id)
        serializer = PaymentProgressSerializer(progress)
        return Response(serializer.data)
