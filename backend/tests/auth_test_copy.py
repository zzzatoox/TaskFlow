import pytest
from httpx import AsyncClient, ASGITransport
import jwt

from backend.app.main import app
from backend.app.config import settings

BASE_URL = "http://testserver"

# Тестовые учетные данные
TEST_USER_DATA = {
    "login": "testuser",
    "email": "testuser@mail.ru",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "last_name": "Test",
    "first_name": "User",
    "patronymic": "Test",
}


@pytest.mark.anyio
async def test_successful_login():
    """Тест успешной аутентификации с правильными учетными данными"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # 1. Регистрируем пользователя
        register_response = await ac.post(
            "/users",
            json=TEST_USER_DATA,
        )
        assert register_response.status_code == 200

        # 2. Логинимся с правильными учетными данными
        login_response = await ac.post(
            "/token",
            data={
                "username": TEST_USER_DATA["login"],
                "password": TEST_USER_DATA["password"],
            },
        )

        assert login_response.status_code == 200
        token_data = login_response.json()

        # 3. Проверяем структуру ответа
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"

        # 4. Проверяем, что токен - валидный JWT
        assert isinstance(token_data["access_token"], str)
        assert len(token_data["access_token"]) > 0

        # 5. Декодируем токен и проверяем содержимое
        decoded_token = jwt.decode(
            token_data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert decoded_token["sub"] == TEST_USER_DATA["login"]
        assert "exp" in decoded_token  # Проверяем, что есть время истечения


@pytest.mark.anyio
async def test_login_with_incorrect_password():
    """Тест входа с неправильным паролем"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # 1. Регистрируем пользователя
        register_response = await ac.post(
            "/users",
            json=TEST_USER_DATA,
        )
        assert register_response.status_code == 200

        # 2. Пытаемся логиниться с неправильным паролем
        login_response = await ac.post(
            "/token",
            data={
                "username": TEST_USER_DATA["login"],
                "password": "WrongPassword123!",
            },
        )

        # 3. Проверяем, что получили ошибку 401 (Unauthorized)
        assert login_response.status_code == 401


@pytest.mark.anyio
async def test_login_with_nonexistent_user():
    """Тест входа с несуществующим пользователем"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # Пытаемся логиниться с несуществующим логином
        login_response = await ac.post(
            "/token",
            data={
                "username": "nonexistentuser",
                "password": "Password123!",
            },
        )

        # Проверяем, что получили ошибку 401 (Unauthorized)
        assert login_response.status_code == 401


@pytest.mark.anyio
async def test_login_with_empty_credentials():
    """Тест входа с пустыми учетными данными"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # Пытаемся логиниться с пустым логином
        login_response = await ac.post(
            "/token",
            data={
                "username": "",
                "password": TEST_USER_DATA["password"],
            },
        )

        # Проверяем, что получили ошибку
        assert login_response.status_code == 401


@pytest.mark.anyio
async def test_token_expires():
    """Тест, что токен имеет правильное время истечения"""
    from datetime import datetime, timezone

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # 1. Регистрируем пользователя
        register_response = await ac.post(
            "/users",
            json=TEST_USER_DATA,
        )
        assert register_response.status_code == 200

        # 2. Получаем токен
        login_response = await ac.post(
            "/token",
            data={
                "username": TEST_USER_DATA["login"],
                "password": TEST_USER_DATA["password"],
            },
        )

        assert login_response.status_code == 200
        token_data = login_response.json()

        # 3. Декодируем и проверяем время истечения
        decoded_token = jwt.decode(
            token_data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Преобразуем время истечения из unix timestamp в datetime
        exp_time = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
        current_time = datetime.now(timezone.utc)

        # Проверяем, что токен истечет в будущем
        assert exp_time > current_time

        # Проверяем, что время истечения близко к ожидаемому (в пределах 1 минуты)
        time_diff = (exp_time - current_time).total_seconds()
        expected_expiry_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert abs(time_diff - expected_expiry_seconds) < 60  # Допуск 1 минута


@pytest.mark.anyio
async def test_multiple_logins_same_user():
    """Тест несколько входов одного пользователя получают разные токены"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # 1. Регистрируем пользователя
        register_response = await ac.post(
            "/users",
            json=TEST_USER_DATA,
        )
        assert register_response.status_code == 200

        # 2. Логинимся первый раз
        login_response_1 = await ac.post(
            "/token",
            data={
                "username": TEST_USER_DATA["login"],
                "password": TEST_USER_DATA["password"],
            },
        )
        assert login_response_1.status_code == 200
        token_1 = login_response_1.json()["access_token"]

        # 3. Логинимся второй раз
        login_response_2 = await ac.post(
            "/token",
            data={
                "username": TEST_USER_DATA["login"],
                "password": TEST_USER_DATA["password"],
            },
        )
        assert login_response_2.status_code == 200
        token_2 = login_response_2.json()["access_token"]

        # 4. Проверяем, что токены разные (потому что разные время создания)
        # но содержат одинаковый логин
        decoded_token_1 = jwt.decode(
            token_1,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        decoded_token_2 = jwt.decode(
            token_2,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        assert decoded_token_1["sub"] == decoded_token_2["sub"]
        # Токены должны быть разные из-за разного времени создания
        assert token_1 != token_2
