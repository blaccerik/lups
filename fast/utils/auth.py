from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from database.postgres_database import get_postgres_db
from schemas.auth import User, Userv2
from services.chat_service import read_user

oauth2_scheme = HTTPBearer()

YOUR_CLIENT_ID = '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com'
TEST_CREDENTIALS = "erik"

async def get_user_v2(
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
        postgres_client: Session = Depends(get_postgres_db)) -> Userv2:
    try:
        if credentials.credentials == TEST_CREDENTIALS:
            google_id = "1234567890123456789012345"
            name = "erik"
        else:
            id_info = id_token.verify_oauth2_token(credentials.credentials, requests.Request(), YOUR_CLIENT_ID)
            google_id = id_info.get('sub')
            name = id_info.get("name")
    except Exception as e:
        print(f"auth.py {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user_id = read_user(User(google_id=google_id, name=name), postgres_client)
    return Userv2(google_id=google_id, name=name, user_id=user_id)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        id_info = id_token.verify_oauth2_token(credentials.credentials, requests.Request(), YOUR_CLIENT_ID)
        google_id = id_info.get('sub')
        name = id_info.get("name")
    except Exception as e:
        print(f"auth.py {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return User(google_id=google_id, name=name)


async def get_current_user_with_token(credentials: str):
    if credentials == "":
        return None
    try:
        id_info = id_token.verify_oauth2_token(credentials, requests.Request(), YOUR_CLIENT_ID)
        google_id = id_info.get('sub')
        name = id_info.get("name")
    except Exception as e:
        print(f"auth.py {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return User(google_id=google_id, name=name)
