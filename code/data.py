# Пример json для возврата
searchResponse = {
  "search_id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da",
  "status": "PENDING",
  "items": []
}

bookingResponse1 = {
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

bookingResponse2 = {
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


offerResponse = {
  "id": "3c0d66ca-47e2-4e4e-9c9f-21b774b64a7f",
  "flights": [
    {
      "duration": 18000,
      "segments": [
        {
          "operating_airline": "DV",
          "flight_number": "828",
          "equipment": "Airbus A320-100/200",
          "cabin": "Economy",
          "dep": {
            "at": "2022-02-09T03:05:00+06:00",
            "airport": {
              "code": "ALA",
              "name": "Алматы"
            },
            "terminal": "4"
          },
          "arr": {
            "at": "2022-02-09T05:55:00+06:00",
            "airport": {
              "code": "CIT",
              "name": "Шымкент"
            },
            "terminal": "1"
          },
          "baggage": "1PC"
        },
        {
          "operating_airline": "DV",
          "flight_number": "958",
          "equipment": "Boeing 767-200",
          "cabin": "Economy",
          "dep": {
            "at": "2022-02-09T09:15:00+06:00",
            "airport": {
              "code": "CIT",
              "name": "Шымкент"
            },
            "terminal": "3"
          },
          "arr": {
            "at": "2022-02-09T11:25:00+06:00",
            "airport": {
              "code": "NQZ",
              "name": "Нур-Султан (Астана)"
            },
            "terminal": "4"
          },
          "baggage": "1PC"
        }
      ]
    }
  ],
  "price": {
    "amount": 87736,
    "currency": "KZT"
  },
  "refundable": True,
  "baggage": "1PC",
  "cabin": "Economy",
  "type": "OW",
  "airline": {
    "code": "DV",
    "name": "SCAT",
    "logo": {
      "url": "http://localhost/img/5661-501f546c73c976a96cf0d18e600b4d7a.gif",
      "width": 1416,
      "height": 274
    }
  },
  "passengers": {
    "ADT": 1,
    "CHD": 0,
    "INF": 0
  }
}

