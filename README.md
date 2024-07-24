## Payment_system

# Технологии:

* DRF
* Celery
* PostgreSQL

# Установка и запуск

## Docker

Расположение `.env`.
```
└── backend/                  
    └── api/ 
    └── ...          
    └── requirements.txt
    └── .env         
├── ... 
├── docker-compose.yml
├── .env
```

Структура файла `backend/.env` . Для запуска вне Docker'а - поменять ключ DOCKER на `False`.
```
DB_USERNAME = 'postgres'
DB_PASSWORD = 'qasaq123'
DB_NAME = 'homedb'
DB_HOST = 'postgres'
DB_PORT = 5432

SECRET_KEY = 'django-insecure-r_6q@95!-3r$=a$x&jo&lfe_6kds^g1qv$p*p2x0gyp(u)cnm('

DOCKER  = True

CELERY_RESULT_BACKEND_DOCKER = 'redis://redis:6379/0'
CELERY_BROKER_URL_DOCKER = 'redis://redis:6379/0'

CELERY_RESULT_BACKEND_LOCAL = 'redis://127.0.0.1:6379/0'
CELERY_BROKER_URL_LOCAL = 'redis://127.0.0.1:6379/0'
```

Структура `.env`:
```
DB_USERNAME='postgres'
DB_PASSWORD='qasaq123'
DB_NAME='homedb'
DB_PORT='postgres'
```


```
docker compose -f docker-compose.yml up --build
docker compose -f docker-compose.yml exec backend python3 manage.py makemigrations
docker compose -f docker-compose.yml exec backend python3 manage.py migrate
docker compose -f docker-compose.yml exec backend python3 manage.py createsuperuser
docker compose -f docker-compose.yml exec backend python3 manage.py create_test_data
docker compose -f docker-compose.yml exec backend python3 manage.py collectstatic
```


## Ручная установка

### Установка зависимостей:
```
python -m venv env
source env/Script/Activate
pip install -r backend/requirements.txt
```

### Миграции:
```
python manage.py makemigrations
python manage.py migrate

# Заполнить DB данными
python manage.py create_test_data
```

### Запуск celery
```
celery -A payment_system worker --loglevel=info -P eventlet
```



# Эндпоинты:


### GET /api/homes/
Получение списка всех домов.

Ответ:

`200 OK`: Возвращает список всех домов.


Пример:
```
 {
        "house_number": 1,
        "street": {
            "street_name": "Первая улица"
        },
        "flats": [
            {
                "flat_number": 1,
                "flat_size": 90.3072359239811,
                "water_checkers_count": 2
            },
            ...
            {
                "flat_number": 10,
                "flat_size": 35.77,
                "water_checkers_count": 3
            },
            

        ]
 }
```


### GET /api/homes/details/
Получение информации о доме по его номеру и названию улицы.

Параметры (body):

* home_number: Номер дома (обязательный)
* street_name: Название улицы (обязательный)

Ответ:

* `200 OK`: Возвращает информацию о доме.
* `400 Bad Request`: Необходимы параметры home_number и street_name.
* `404 Not Found`: Дом не найден.

Пример ответа: 
```
{
    "house_number": 1,
    "street": {
        "street_name": "Первая улица"
    },
    "flats": [
        {
            "flat_number": 1,
            "flat_size": 90.3072359239811,
            "water_checkers_count": 2
        },
        ...
        {
            "flat_number": 10,
            "flat_size": 39.380878741644025,
            "water_checkers_count": 2
        }
    ]
}
```

### PUT /api/homes/details/?params
Обновление информации о доме по его номеру и названию улицы.

Параметры (body):

* home_number: Номер дома (обязательный)
* street_name: Название улицы (обязательный)
* Поля для обновления.

Пример ответа:
```
{
    "house_number": 1,
    "street": {
        "street_name": "Ул. Новая"
    },
    "flats": [
        {
            "flat_number": 1,
            "flat_size": 50.0
        },
        {
            "flat_number": 2,
            "flat_size": 60.0
        }
    ]
}
```
Ответ:

* `200 OK`: Возвращает обновленную информацию о доме.
* `400 Bad Request`: Ошибка валидации данных.
* `404 Not Found`: Дом не найден.




### DELETE /api/homes/details/?params
Удаление дома по его номеру и названию улицы.

Параметры (body):

* home_number: Номер дома (обязательный)
* street_name: Название улицы (обязательный)

Ответ:

* `204 No Content`: Дом успешно удален.
* `404 Not Found`: Дом не найден.


### POST /api/homes/create/
Создание нового дома.

Параметры (body):

* home_number: Номер дома
* street_name: Название улицы
* flats: (list)

Ответ:

* `201 Created`: Возвращает созданный дом.
* `400 Bad Request`: Ошибка валидации данных.


### POST /api/water-checkers/create/
Создание нового счетчика воды.

Параметры (form-data):

* home: Номер дома
* flats: Номера квартир через запятую
* year: Год
* month: Месяц 
* water_amount: Показания счетчика

Ответ:

* `201 Created`: Возвращает созданный счетчик воды.
* `400 Bad Request`: Ошибка валидации данных.

Пример ответа: 
```
{
    "home": 1,
    "flat": 1,
    "year": 2024,
    "month": 7,
    "water_amount": 220.0
}
```

### GET /api/water-checkers/details/
Получение информации о счетчиках воды.

Параметры (form-data):

* home: Номер дома (необязательный)
* flats: Номера квартир через запятую (необязательный)
* year: Год (необязательный)
* month: Месяц (необязательный)

Ответ:

* `200 OK`: Возвращает информацию о счетчиках воды.
* `404 Not Found`: Счетчики воды не найдены.

Пример ответа: 
```
[
    {
        "home": 1,
        "flat": 1,
        "year": 2024,
        "month": 7,
        "water_amount": 220.0
    },
    {
        "home": 1,
        "flat": 2,
        "year": 2024,
        "month": 7,
        "water_amount": 111.0
    }
]
```


### POST /payment/calculate/
Запускает задачу расчёта квартплаты и сохраняет прогресс выполнения задачи.

Параметры (body):

* home_number: Номер дома.
* street_name: Название улицы.
* month: Месяц расчёта.
* year: Год расчёта.


Ответ:

* `201 Created`: Возвращает task_id запущенной задачи.

Пример запроса:
```
{
    "home_number": 1,
    "street_name": "Первая улица",
    "month": 5,
    "year": 2023
}
```

Пример ответа:

```
{
    "task_id": "task_id"
}
```

### GET /payment/progress/<task_id>/
Получить статус выполнения задачи расчёта квартплаты по task_id.

Параметры:

* task_id: ID задачи

Ответ:

* `200 OK`: Возвращает статус выполнения и результат задачи.
* `404 Not Found`: Задача не найдена.

Пример ответа:

```
{
    "task_id": "6a52ebe3-debb-460b-a811-d47b5f75c653",
    "home": {
        "house_number": 1,
        "street": {
            "street_name": "Первая улица"
        }
    },
    "month": 3,
    "year": 2023,
    "result": "32472.80000000001",
    "status": "COMPLETED",
    "flat_payments": [
        {
            "flat_number": "1",
            "water_consumption": 266.3000000000002,
            "water_cost": 798.9000000000005,
            "maintenance_cost": 354.0,
            "total_cost": 1152.9000000000005
        },
        {
            "flat_number": "2",
            "water_consumption": 649.6999999999989,
            "water_cost": 1949.0999999999967,
            "maintenance_cost": 220.0,
            "total_cost": 2169.0999999999967
        },

        ...

                {
            "flat_number": "10",
            "water_consumption": 1316.1000000000004,
            "water_cost": 3948.300000000001,
            "maintenance_cost": 264.5,
            "total_cost": 4212.800000000001
        }
    ]
}
```