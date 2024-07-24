from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from home.models import Home, WaterChecker, Flat
from .serializers import (
    HomeSerializer,
    HomeCreateUpdateSerializer,
    WaterCheckerSerializer
)


class HomeListView(APIView):
    '''
    Получаем список всех домов.

    GET:
    Возвращает список всех домов.
    '''

    def get(self, request):
        homes = Home.objects.all()
        serializer = HomeSerializer(homes, many=True)
        return Response(serializer.data)


class HomeDetailView(APIView):
    '''
    Получаем, обновляем или удаляем конкретный дом.

    GET:
    Возвращает данные о конкретном доме,
    используя параметры `home_number` и `street_name`.

    PUT:
    Обновляет данные о конкретном доме.

    DELETE:
    Удаляет конкретный дом.

    '''

    def get(self, request):
        home_number = request.data.get('home_number')
        street_name = request.data.get('street_name')

        if not home_number or not street_name:
            return Response({'error':
                             'Необходимы параметры:home_number и street_name'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            home = get_object_or_404(
                Home,
                house_number=home_number,
                street__street_name=street_name
            )
        except Home.DoesNotExist:
            return Response({'error': 'Дом не найден'},
                            status=status.HTTP_404_NOT_FOUND
                            )

        serializer = HomeSerializer(home)
        return Response(serializer.data)

    def put(self, request):
        home_number = request.data.get('home_number')
        street_name = request.data.get('street_name')
        if not home_number or not street_name:
            return Response({'error':
                             'Необходимы параметры:home_number и street_name'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            home = get_object_or_404(
                Home,
                house_number=home_number,
                street__street_name=street_name
            )
        except Home.DoesNotExist:
            return Response({'error': 'Дом не найден'},
                            status=status.HTTP_404_NOT_FOUND
                            )

        serializer = HomeCreateUpdateSerializer(home, data=request.data,
                                                partial=True
                                                )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        home_number = request.query_params.get('home_number')
        street_name = request.query_params.get('street_name')
        if not home_number or not street_name:
            return Response({'error':
                             'Необходимы параметры:home_number и street_name'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            home = get_object_or_404(
                Home,
                house_number=home_number,
                street__street_name=street_name
            )
        except Home.DoesNotExist:
            return Response({'error': 'Дом не найден'},
                            status=status.HTTP_404_NOT_FOUND
                            )
        home.delete()
        return Response({'message': 'Дом удален'},
                        status=status.HTTP_204_NO_CONTENT
                        )


class HomeCreateView(APIView):
    '''

    Создаем новый дом.

    POST:
    Создает новый дом с переданными данными.

    '''

    def post(self, request):
        serializer = HomeCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            home = serializer.save()
            response_serializer = HomeCreateUpdateSerializer(home)
            return Response(response_serializer.data,
                            status=status.HTTP_201_CREATED
                            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaterCheckerCreateView(APIView):
    '''

    Создаем новую запись счетчика воды.

    POST:
    Создает новую запись счетчика воды с переданными данными.

    '''

    def post(self, request):
        serializer = WaterCheckerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaterCheckerDetailView(APIView):
    '''

    Получаем данные о счетчиках воды.

    GET:
    Возвращает данные о счетчиках воды, используя фильтры по номеру дома,
    номерам квартир, году и месяцу.

    '''

    def get(self, request):
        home_number = request.data.get('home')
        flat_numbers = request.data.get('flats')
        year = request.data.get('year')
        month = request.data.get('month')

        filters = {}

        if home_number:
            try:
                home = Home.objects.get(house_number=home_number)
                filters['home'] = home
            except Home.DoesNotExist:
                return Response({'error': 'Дом не найден'},
                                status=status.HTTP_404_NOT_FOUND
                                )

        if flat_numbers:
            flat_numbers_list = flat_numbers.split(',')
            try:
                flats = Flat.objects.filter(flat_number__in=flat_numbers_list)
                filters['flat__in'] = flats
            except Flat.DoesNotExist:
                return Response({'error':
                                 'Одна или несколько квартир не найдены'},
                                status=status.HTTP_404_NOT_FOUND
                                )

        if year:
            filters['year'] = year

        if month:
            filters['month'] = month

        try:
            water_checkers = WaterChecker.objects.filter(**filters)
        except WaterChecker.DoesNotExist:
            return Response({'error': 'Счетчики воды не найдены'},
                            status=status.HTTP_404_NOT_FOUND
                            )

        serializer = WaterCheckerSerializer(water_checkers, many=True)
        return Response(serializer.data)
