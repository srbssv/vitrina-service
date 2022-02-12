# Веб-сервис Витрина

## Инструкции для запуска без Docker

1. Клонируем репозиторий и переходим в корневую директорию проекта
```bash
git clone https://gitlab.com/internship2022/team-of-denis/aitugan/project.git
cd project
```
2. Создаем изолированную среду python, например с помощью [virtualenv](https://pypi.org/project/virtualenv)
```bash
virtualenv .venv
source .venv/bin/activate
```
3. Устанавливаем нужные пакеты через pip
```bash
pip install -r requirements/dev.txt
```
4. Запускаем веб сервис
```bash
python code/app.py
```
5. Увидим в консоли текст как ниже.  
```bash
[2022-01-30 20:57:07 +0600] [11880] [INFO] 
  ┌───────────────────────────────────────────────────────────────────────────────┐
  │                                 Sanic v21.12.1                                │
  │                        Goin Fast @ http://0.0.0.0:8000                       │
  ├───────────────────────┬───────────────────────────────────────────────────────┤
  │                       │     mode: production, single worker                   │
  │     ▄███ █████ ██     │   server: sanic                                       │
  │    ██                 │   python: 3.10.1                                      │
  │     ▀███████ ███▄     │ platform: Linux-5.15.11-arch2-1-x86_64-with-glibc2.33 │
  │                 ██    │ packages: sanic-routing==0.7.2                        │
  │    ████ ████████▀     │                                                       │
  │                       │                                                       │
  │ Build Fast. Run Fast. │                                                       │
  └───────────────────────┴───────────────────────────────────────────────────────┘

[2022-01-30 20:57:07 +0600] [11880] [WARNING] Sanic is running in PRODUCTION mode. Consider using '--debug' or '--dev' while actively developing your application.
[2022-01-30 20:57:07 +0600] [11880] [INFO] Starting worker [11880]
```

## Инструкции для запуска с докером

1. Клонируем репозиторий и переходим в корневую директорию проекта
```bash
git clone https://gitlab.com/internship2022/team-of-denis/aitugan/project.git
cd project
```
2. С помощью [docker-compose](https://docs.docker.com/compose/install/) собираем сервис.
```bash
docker-compose build
```
3. Поднимаем сервис
```bash
docker-compose up
```

## Эндпоинты и типы запросов

### **Поиск**

  - **GET** /search
  
  Возвращает ответ в формате JSON:
  ```json
{
    "search_id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da",
    "status": "PENDING",
    "items": []
}
  ```


   - **POST** /search
  
  Принимает на вход JSON:
  ```json
{
  "provider": "Amadeus",
  "cabin": "Economy",
  "origin": "ALA",
  "destination": "NQZ",
  "dep_at": "2022-02-09",
  "arr_at": "2022-02-15",
  "adults": 1,
  "children": 0,
  "infants": 0,
  "currency": "KZT"
}
  ```

Возвращает следующие данные:
```json
{
    "search_id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da",
    "status": "PENDING",
    "items": []
}
```

### **Бронирование**

  - **GET** /booking
Возвращает данные формата JSON:
```json
{
  "id": "ecdea60d-4b85-4f8b-98d0-4da07bb02f99",
  "pnr": "HKBTXK",
  "expires_at": "2022-01-23T15:10:14.411858+06:00",
  "phone": "+77013748830",
  "email": "example@mail.com",
  "offer": {
    "id": "826cf3e2-ea2a-4ee3-928a-3ded2b025a39",
    "flights": [
      {
        "duration": 12600,
        "segments": [
          {
            "operating_airline": "KC",
            "flight_number": "918",
            "equipment": "Airbus A320-200 Sharklet",
            "cabin": "Economy",
            "dep": {
              "at": "2022-02-09T03:00:00+06:00",
              "airport": {
                "code": "ALA",
                "name": "Алматы"
              },
              "terminal": "4"
            },
            "arr": {
              "at": "2022-02-09T02:25:00+05:00",
              "airport": {
                "code": "GUW",
                "name": "Атырау"
              },
              "terminal": "4"
            },
            "baggage": "1PC"
          },
          {
            "operating_airline": "KC",
            "flight_number": "617",
            "equipment": "Airbus A319-100 Sharklets",
            "cabin": "Economy",
            "dep": {
              "at": "2022-02-09T06:15:00+05:00",
              "airport": {
                "code": "GUW",
                "name": "Атырау"
              },
              "terminal": "1"
            },
            "arr": {
              "at": "2022-02-09T10:20:00+06:00",
              "airport": {
                "code": "NQZ",
                "name": "Нур-Султан (Астана)"
              },
              "terminal": "7"
            },
            "baggage": "1PC"
          }
        ]
      }
    ],
    "price": {
      "amount": 79522,
      "currency": "KZT"
    },
    "refundable": True,
    "baggage": "1PC",
    "cabin": "Economy",
    "airline": {
      "code": "KC",
      "name": "Air Astana",
      "logo": {
        "url": "http://localhost/img/3093-fe65813d49024ba21b9ac7e21781fad5.svg"
      }
    },
    "passengers": {
      "ADT": 1,
      "CHD": 0,
      "INF": 0
    },
    "type": "OW"
  },
  "passengers": [
    {
      "gender": "M",
      "type": "ADT",
      "first_name": "CRAIG",
      "last_name": "BENSEN",
      "date_of_birth": "1987-02-22",
      "citizenship": "KZ",
      "document": {
        "number": "1341234234",
        "expires_at": "2025-02-22",
        "iin": "123456789123"
      }
    }
  ]
}
```

- **POST** /booking

Тело запроса в формате JSON:
```json 
{
  "offer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "phone": "+77777777777",
  "email": "user@example.com",
  "passengers": [
    {
      "gender": "M",
      "type": "ADT",
      "first_name": "CRAIGE",
      "last_name": "BENSEN",
      "date_of_birth": "1987-01-24",
      "citizenship": "US",
      "document": {
        "number": "N234346356",
        "expires_at": "2025-01-24",
        "iin": "123456789123"
      }
    }
  ]
}

```

Возвращает ответ JSON:
```json
{
  "id": "ecdea60d-4b85-4f8b-98d0-4da07bb02f99",
  "pnr": "HKBTXK",
  "expires_at": "2022-01-23T15:10:14.411858+06:00",
  "phone": "+77013748830",
  "email": "example@mail.com",
  "offer": {},
  "passengers": [
    {
      "gender": "M",
      "type": "ADT",
      "first_name": "CRAIG",
      "last_name": "BENSEN",
      "date_of_birth": "1987-02-22",
      "citizenship": "KZ",
      "document": {
        "number": "1341234234",
        "expires_at": "2025-02-22",
        "iin": "123456789123"
      }
    }
  ]
}
```
