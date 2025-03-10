# book_store
Фильнальный проект по python ШАД МТС.

# Запуск проекта
Используется python версии 3.12.

## Установка зависимостей
В качестве пакетного менеджера используется pdm. Установка pdm и его активация
```bash
pip install pd
pdm sync
eval $(pdm venv activate)
```
## Запуск базы данных
### Для dev окружения:
Для разработки, необходимо развернуть только базу данных и применить миграции. В dev окружении приложение не будет запущено (или будет работать с использованием тестового сервера).
1. Заполнить .env по примеру example.env
    ```
        POSTGRES_DB=<pg_db:str>
        POSTGRES_USER=<pg_db:str>
        POSTGRES_PASSWORD=<pg_db:str>
        POSTGRES_HOST=<ip:port>

        SECRET_KEY=<str>
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=<int>
    ```
2. Разверните контейнеры с помощью docker-compose:
    ```bash
        docker-compose up
    ```
3. Примените миграции с помощью Alembic:
    ```bash
        alembic upgrade head
    ```
4. Для поднятия локально fastapi без docker:
    ```bash
        cd src
        fastapi dev main.py
    ```