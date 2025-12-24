# Profiles

---

## Запуск

### Запуск с Docker Compose

```bash
docker compose -f docker-compose.dev.yml up --build
```

> Запуск `profiles` произойдёт **только после успешного прохождения всех тестов**.

### Запуск тестов отдельно

```bash
docker compose -f docker-compose.dev.yml up --build profiles-test
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
| `GRANIAN_LOG_LEVEL` | уровень логирования (`critical`, `error`, `warning`, `info`, `debug`, `trace`) |

#### PostgreSQL

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

#### Profiles

| Переменная    | Описание                                                                                                                   |
|---------------|:---------------------------------------------------------------------------------------------------------------------------|
| `PG_USER`     | Пользователь БД для подключения                                                                                            |
| `PG_PASSWORD` | Пароль пользователя БД                                                                                                     |
| `PG_HOST`     | Хост PostgreSQL (при docker-compose указывать `postgres`)                                                                  |
| `DEBUG`       | Режим отладки. Возможные значения: `true`/`false`, `True`/`False`, `1`/`0`, `yes`/`no`, `Yes`/`No`, `on`/`off`, `On`/`Off` |
| `LOG_LEVEL`   | уровень логирования (`critical`, `error`, `warning`, `info`, `debug`, `trace`)                                             |

Подробнее см. в [`app/config.py`](./app/config.py) и [`.env-example`](./.env-example).

## Архитектура

```
profiles/
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
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── media.py
│   │   └── user.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── media.py
│   │   └── profiles.py
│   ├── schemas.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── media.py
│   │   └── profiles.py
│   └── utils
│       └── auth.py
├── docker-compose.dev.yml
├── requirements
│   ├── prod.txt
│   └── test.txt
├── test.Dockerfile
└── tests
    ├── conftest.py
    ├── test_media.py
    └── test_profiles.py
```