import jwt
from datetime import datetime, timedelta

from fastapi import Depends

SECRET_KEY = "13R2FMzNRSCXqg9zJCll"
ALGORITHM = "HS256"


def create_jwt_token(data: dict,EXPIRATION_TIME):
    expiration = datetime.utcnow() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None
