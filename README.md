# Contacts REST API (goit-pythonweb-hw-08)

REST API для зберігання та управління контактами, побудований на **FastAPI**, **SQLAlchemy 2.0** та **PostgreSQL**. Для міграцій використовується **Alembic**, для валідації — **Pydantic v2**.

## Функціональність

- CRUD для контактів (`/api/contacts`)
- Пошук за іменем, прізвищем або email через query-параметри
- Ендпоінт контактів з днями народження на найближчі 7 днів (налаштовується `days`)
- Swagger UI: `/docs`, ReDoc: `/redoc`

## Модель Contact

| Поле              | Тип      | Обов'язкове |
|-------------------|----------|-------------|
| `first_name`      | string   | так         |
| `last_name`       | string   | так         |
| `email`           | email    | так, унікальне |
| `phone`           | string   | так         |
| `birthday`        | date     | так         |
| `additional_info` | string   | ні          |

## Швидкий старт

### 1. Клонувати репозиторій та створити `.env`

```bash
cp .env.example .env
```

### 2. Запустити PostgreSQL

```bash
docker compose up -d
```

### 3. Встановити залежності

```bash
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

### 4. Застосувати міграції

```bash
alembic upgrade head
```

### 5. Запустити застосунок

```bash
python main.py
# або
uvicorn main:app --reload
```

Swagger-документація: <http://localhost:8000/docs>

## Ендпоінти

| Метод  | Шлях                                  | Опис                                         |
|--------|---------------------------------------|----------------------------------------------|
| GET    | `/api/contacts/`                      | Список контактів + фільтри `first_name`, `last_name`, `email`, пагінація `skip`, `limit` |
| GET    | `/api/contacts/upcoming-birthdays`    | Контакти з ДН на найближчі `days` днів (за замовчуванням 7) |
| GET    | `/api/contacts/{id}`                  | Отримати контакт за id                       |
| POST   | `/api/contacts/`                      | Створити контакт                             |
| PUT    | `/api/contacts/{id}`                  | Оновити контакт                              |
| DELETE | `/api/contacts/{id}`                  | Видалити контакт                             |

## Приклад запиту

```bash
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Content-Type: application/json" \
  -d '{
        "first_name": "Ivan",
        "last_name": "Franko",
        "email": "ivan.franko@example.com",
        "phone": "+380501234567",
        "birthday": "1990-05-17",
        "additional_info": "Письменник"
      }'
```

## Структура проєкту

```
goit-pythonweb-hw-08/
├── main.py
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── .env.example
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_create_contacts_table.py
└── src/
    ├── api/contacts.py
    ├── conf/config.py
    ├── database/{db.py, models.py}
    ├── repository/contacts.py
    └── schemas/contacts.py
```

## Нові міграції

```bash
alembic revision --autogenerate -m "описова назва"
alembic upgrade head
```
