# API-gateway

---

## Запуск

### Запуск с Docker Compose

```bash
docker compose -f docker-compose.dev.yml up --build
```

> Запуск `api-gateway` произойдёт **только после успешного прохождения всех тестов**.

### Запуск тестов отдельно

```bash
docker compose -f docker-compose.dev.yml up --build api-gateway-test
```

---

## Конфигурация

Перед запуском создайте файл `.env` на основе примера:

```bash
cp .env-example .env
```

### Переменные окружения

#### Granian

| Переменная          | Описание                                                                       |
|---------------------|:-------------------------------------------------------------------------------|
| `HOST`              | Адрес прослушивания (по умолчанию `0.0.0.0`)                                   |
| `PORT`              | Порт (по умолчанию `8000`)                                                     |
| `WORKERS`           | Количество воркеров/процессов (по умолчанию `1`)                               |
| `GRANIAN_LOG_LEVEL` | Уровень логирования (`critical`, `error`, `warning`, `info`, `debug`, `trace`) |

#### PostgreSQL (`user-db`)

| Переменная      | Описание                                                                                               |
|-----------------|--------------------------------------------------------------------------------------------------------|
| `PG_ADMIN`      | Администратор базы данных                                                                              |
| `PG_ADMIN_PASS` | Пароль администратора                                                                                  |
| `PG_DB_NAME`    | Название базы данных                                                                                   |
| `PG_PORT`       | Порт PostgreSQL (по умолчанию `5432`)                                                                  |
| `POOL_SIZE`     | Размер пула подключений (по умолчанию `10`)                                                            |
| `MAX_OVERFLOW`  | Максимальное количество временных соединений (по умолчанию `20`)                                       |
| `POOL_TIMEOUT`  | Максимальное время ожидания свободного соединения из пула (pytimeparse формат, пример: `'30 seconds'`) |
| `POOL_RECYCLE`  | Максимальное время жизни соединения (pytimeparse формат, пример: `'30 minutes'`)                       |

#### API-gateway

| Переменная                | Описание                                                                                                                   |
|---------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| `PG_USER`                 | Пользователь БД для подключения                                                                                            |
| `PG_PASSWORD`             | Пароль пользователя БД                                                                                                     |
| `PG_HOST`                 | Хост PostgreSQL (при docker-compose указывать `postgres`)                                                                  |
| `JWT_SECRET_KEY`          | Секретный ключ JWT (**минимум 32 символа**)                                                                                |
| `JWT_ALGORITHM`           | Алгоритм подписи JWT (по умолчанию `HS256`). Возможные значения: `HS256`, `HS384`, `HS512`                                 |
| `ACCESS_TOKEN_EXPIRE`     | Время жизни access-токена (pytimeparse формат, пример: `'15 minutes'`)                                                     |
| `REFRESH_TOKEN_EXPIRE`    | Время жизни refresh-токена (pytimeparse формат, пример: `'30 days'`)                                                       |
| `PASSWORD_HASH_ALGORITHM` | Алгоритм хэширования паролей (по умолчанию `bcrypt`). Возможные значения: `bcrypt`, `argon2`, `pbkdf2_sha256`              |
| `ALLOWED_ORIGINS`         | Список разрешённых источников для CORS (JSON, пример: `["*"]`, если не указан - отключен)                                  |
| `MICRO_SERVICES`          | Маппинг сервисов и их адресов (JSON, пример: `{"service1":"http://...}"`)                                                  |
| `LOG_LEVEL`               | Уровень логирования (`critical`, `error`, `warning`, `info`, `debug`, `trace`)                                             |
| `DEBUG`                   | Режим отладки. Возможные значения: `true`/`false`, `True`/`False`, `1`/`0`, `yes`/`no`, `Yes`/`No`, `on`/`off`, `On`/`Off` |

Подробнее см. в [`app/config.py`](./app/config.py) и [`.env-example`](./.env-example).

## Архитектура

```
api-gateway/
├── .env
├── .env-example
├── README.md
├── api.Dockerfile
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   ├── logs.py
│   ├── main.py
│   ├── models.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── proxy.py
│   ├── schemas.py
│   ├── services
│   │   ├── auth.py
│   │   └── proxy.py
│   └── utils
│       └── auth.py
├── docker-compose.dev.yml
├── requirements
│   ├── prod.txt
│   └── test.txt
├── test.Dockerfile
└── tests
    ├── conftest.py
    ├── test_auth.py
    └── test_proxy.py
```