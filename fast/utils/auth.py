import fastapi.security
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token
from datetime import datetime, timedelta
from typing import Annotated

from schemas.schemas import User
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme = HTTPBearer()

YOUR_CLIENT_ID = '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com'


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        id_info = id_token.verify_oauth2_token(credentials.credentials, requests.Request(), YOUR_CLIENT_ID)
        google_id = id_info.get('sub')
        name = id_info.get("name")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return User(google_id=google_id, name=name)