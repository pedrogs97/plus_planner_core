"""Unit tests for the service module."""

from datetime import datetime, timedelta

import jwt
import pytest

from src.auth.service import (
    get_new_token,
    get_refresh_token,
    get_user_by_token,
    hash_password,
    login,
    logout,
    password_is_correct,
    token_is_valid,
)
from src.config import ACCESS_TOKEN_EXPIRE_HOURS, ALGORITHM, SECRET_KEY


def test_password_is_correct_success():
    """Test password_is_correct function. Success"""
    hashed_password = hash_password("password")
    assert password_is_correct("password", hashed_password) is True


def test_password_is_correct_fail():
    """Test password_is_correct function. Fail"""
    hashed_password_invalid = hash_password("password_invalid")
    assert password_is_correct("password", hashed_password_invalid) is False


def test_hash_password():
    """Test hash_password function"""
    hashed_password = hash_password("password")
    assert hashed_password != "password"
    assert len(hashed_password) == 60
    assert password_is_correct("password", hashed_password) is True


@pytest.mark.asyncio
async def test_get_new_token(user_fixture):
    """Test get_new_token function"""
    user = user_fixture
    keys = [
        "accessToken",
        "refreshToken",
        "tokenType",
        "expiresAt",
    ]
    dict_token = await get_new_token(user)
    assert all(key in dict_token.keys() for key in keys)


def test_token_is_valid_dict_success():
    """Test token_is_valid function. Success"""
    access_expire_in = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_expire_timestamp = int(access_expire_in.timestamp())
    token = {
        "exp": access_expire_timestamp,
        "type": "access",
    }
    assert token_is_valid(token) is True


def test_token_is_valid_dict_fail():
    """Test token_is_valid function. Fail"""
    access_expire_in = datetime.now() - timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_expire_timestamp = int(access_expire_in.timestamp())
    token = {
        "exp": access_expire_timestamp,
        "type": "access",
    }

    assert token_is_valid(token) is False


def test_token_is_valid_model_success(token_valid_fixture):
    """Test token_is_valid function. Success"""
    token = token_valid_fixture

    assert token_is_valid(token) is True


def test_token_is_valid_model_fail(token_invalid_fixture):
    """Test token_is_valid function. Fail"""
    token = token_invalid_fixture

    assert token_is_valid(token) is False


@pytest.mark.asyncio
async def test_get_user_by_token_str_sucess(user_fixture):
    """Test get_user_by_token function. Success"""
    encode = {
        "sub": user_fixture.id,
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_user_by_token(token)
    user_dict = user.__dict__
    user_fixture_dict = user_fixture.__dict__

    assert user is not None
    assert all(user_dict[key] == user_fixture_dict[key] for key in user_dict.keys())


@pytest.mark.asyncio
async def test_get_user_by_token_str_fail():
    """Test get_user_by_token function. Fail"""
    user = await get_user_by_token("invalid token")

    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_token_dict_sucess(user_fixture):
    """Test get_user_by_token function. Success"""
    user = await get_user_by_token({"sub": user_fixture.id})
    user_dict = user.__dict__
    user_fixture_dict = user_fixture.__dict__

    assert user is not None
    assert all(user_dict[key] == user_fixture_dict[key] for key in user_dict.keys())


@pytest.mark.asyncio
async def test_get_user_by_token_dict_fail():
    """Test get_user_by_token function. Fail"""
    user = await get_user_by_token({"sub": 0})

    assert user is None


@pytest.mark.asyncio
async def test_login_success(user_fixture):
    """Test login function. Success"""
    user = user_fixture
    keys = [
        "accessToken",
        "refreshToken",
        "tokenType",
        "expiresAt",
    ]

    dict_token = await login(user.email, "password", None)

    assert all(key in dict_token.keys() for key in keys)


@pytest.mark.asyncio
async def test_login_fail_password(user_fixture):
    """Test login function. Fail password"""
    user = user_fixture

    dict_token = await login(user.email, "password_wrong", None)

    assert dict_token is None


@pytest.mark.asyncio
async def test_login_fail_email():
    """Test login function. Fail email"""

    dict_token = await login("wrong_email", "password", None)

    assert dict_token is None


@pytest.mark.asyncio
async def test_logout(user_fixture):
    """Test logout function"""
    encode = {
        "sub": user_fixture.id,
        "type": "access",
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    await logout(token, None)


@pytest.mark.asyncio
async def test_get_refresh_token_success(user_fixture):
    """Test get_refresh_token function. Success"""
    encode = {
        "sub": user_fixture.id,
        "type": "refresh",
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    keys = [
        "accessToken",
        "refreshToken",
        "tokenType",
        "expiresAt",
    ]

    dict_token = await get_refresh_token(token, None)

    assert all(key in dict_token.keys() for key in keys)


@pytest.mark.asyncio
async def test_get_refresh_token_fail(token_invalid_fixture):
    """Test get_refresh_token function. Fail"""
    dict_token = await get_refresh_token(token_invalid_fixture, None)

    assert dict_token is None
