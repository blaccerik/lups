from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token

from utils.schemas import User

oauth2_scheme = HTTPBearer()

YOUR_CLIENT_ID = '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com'


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
