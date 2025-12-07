import jwt 
from cryptography.fernet import Fernet
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os 
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

env_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))

def generate_password_key():
    key= Fernet.generate_key()
    with open(env_path, mode='a') as f:
        f.write(f'\nPASSWORD_KEY={key}')
    print(key)

#generate_password_key()

load_dotenv(env_path)
password_key= os.environ.get('PASSWORD_KEY')
ALGORITHM= 'HS256'


def create_access_token(user_id:int, expire_at:timedelta= timedelta(minutes=5)) -> str:
    global password_key, ALGORITHM

    exp= datetime.now(timezone.utc) + expire_at

    payload={
        'user_id': user_id,
        'type': 'access',
        'exp': exp.timestamp()
    }

    return jwt.encode(payload, key=password_key, algorithm=ALGORITHM)


def create_refresh_token(user_id:int, expire_at:timedelta= timedelta(days=7)) -> str:
    global password_key, ALGORITHM
    exp= datetime.now(timezone.utc) + expire_at

    payload= {
        'user_id': user_id,
        'type': "refresh",
        'exp': exp.timestamp()
    }

    return jwt.encode(payload, key=password_key, algorithm=ALGORITHM)


def verify_access_token(token:str) -> dict:
    global password_key, ALGORITHM

    try:
        payload= jwt.decode(token, key=password_key, algorithms=[ALGORITHM])

        if payload.get('type') != 'access':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong token type")
        
        return payload
        
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="token is invalid")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired")
    

def verify_refresh_token(token:str) -> dict:
    global password_key, ALGORITHM

    try:
        payload= jwt.decode(token, key=password_key, algorithms=[ALGORITHM])

        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong token type")
        
        return payload
        
    except (jwt.exceptions.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
        return None



oauth_token= OAuth2PasswordBearer(tokenUrl='signin')

def get_user(token=Depends(oauth_token)):
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="token is not found")
    try:
        payload= verify_access_token(token=token)
        user_id= payload.get('user_id')
        return int(user_id)
    
    except (jwt.exceptions.InvalidTokenError, jwt.exceptions.ExpiredSignatureError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't validate the credentials")
    
    
