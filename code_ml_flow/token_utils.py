import os
from datetime import datetime, timedelta
from dependency_injector.providers import Configuration
from typing import Optional, Union
import jwt

from code_ml_flow.error import InvalidTokenError

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"    # should be kept secre


def create_jwt_token(user_id: str, config: Configuration) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "user_id": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, config['auth']['jwt_secret_key'], ALGORITHM)
    return encoded_jwt

def validate_jwt_token(token: str, config: Configuration) -> Union[str, dict]:
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, config['auth']['jwt_secret_key'], algorithms=[ALGORITHM])

        # Check if the token has expired
        if 'exp' in payload:
            expiration_date = datetime.utcfromtimestamp(payload['exp'])
            if expiration_date < datetime.utcnow():
                raise InvalidTokenError("Token has expired")
        return payload["user_id"]

    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.DecodeError:
        raise InvalidTokenError("Invalid token")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")