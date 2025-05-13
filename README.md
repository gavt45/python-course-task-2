## Запуск

Запускаем PG:
```bash
docker run --name todo-gav-postgres -p5432:5432 -e POSTGRES_PASSWORD=postgres -d -e POSTGRES_DB=dbname postgres:15
```

запускаем шел poetry (для простоты) (нужна poetry `pip install poetry`, или можно руками активировать венв при наличии `source .venv/bin/activate`):
```bash
poetry config virtualenvs.in-project true
poetry install 
poetry shell
```

прокатываем миграции:
```bash
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/dbname" alembic -c alembic.ini upgrade head
```

запускаем приложение:
```bash
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/dbname" python3 main.py
```

## Использование

Первым делом нужно зарегаться, это можно сделать через signup endpoint. Никаких парольных политик не проверяется, проверяется только наличие пользователя с юзернеймом. (Если он есть, то получите 409 Конфликт).

После этого авторизоваться можно, нажав на замочек у любого из эндпоинтов (свагер знает, какой эндпоинт нужно дернуть) и введя логин и пароль из предыдущего пункта.

После этого можно проверить создание и пометку тудушки как решенной.

Самое интересное, что я здесь быстро придумал, это использование MAC аутентификации для получения тудушек другого пользователя. В сгенерированной ссылке (эндпоинт получения ссылки генерирует только path без первой части с хостом, считаем что SPA на фронте знает базовый урл приложения) передается nonce сгенерированный рандомно и mac - хэш от ИД пользователя и нонса, т.о без знания секрета нельзя получить ссылку на тудушки пользователя. (Это защита от IDOR уязвимостей)

Перенос тудушек сделан "грязно" просто джобой в apscheduler, которая запускается каждые 10 минут.

Изначально хотел прокидывать юзкейсы через сервис (аля чистая архитектура), но не успел :(

## Migrations

Roll-in migrations:
```shell
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/dbname" alembic -c alembic.ini upgrade head
```

Create revision:
```shell
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/dbname" alembic -c alembic.ini revision --autogenerate -m "revision message"
```

To create or drop enum you need to update migration stage manually, i.e:
```python
sa.Enum('created', 'payed', 'failed', 'active', 'overdue', name='subscriptionstatus').create(op.get_bind())
```