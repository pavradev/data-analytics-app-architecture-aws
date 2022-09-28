from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from passlib.hash import pbkdf2_sha256
import random
import string
from . import database, repository, models
from sqlalchemy.orm import Session

X_API_KEY = APIKeyHeader(name='X-API-Key')


def check_authentication_header(x_api_key: str = Depends(X_API_KEY), db: Session = Depends(database.get_db)):
    """ takes the X-API-Key header and converts it into the matching client id from the database """

    # this is where the SQL query for converting the API key into a user_id will go
    [key_id, secret_key] = x_api_key.split(':')
    user = repository.find_user_by_key_id(db=db, key_id=key_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    if not pbkdf2_sha256.verify(secret_key, user.hashed_secret_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return user


def auth_check(roles: models.Role):
    def decorator_auth(func):
        @wraps(func)
        def wrapper_auth(*args, **kwargs):
            user = kwargs['user']
            if user.role in roles:
                return func(*args, **kwargs)
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"})

        return wrapper_auth
    return decorator_auth


def generate_random_key():
    random_key_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    random_secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=32))
    hashed_secret_key = pbkdf2_sha256.hash(random_secret_key)
    return [random_key_id, random_secret_key, hashed_secret_key]
