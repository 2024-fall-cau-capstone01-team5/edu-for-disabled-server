from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt  # PyJWT 사용
from jwt import PyJWTError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 환경 변수 로드
load_dotenv()

# OAuth2PasswordBearer를 사용하여 토큰 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY 및 ALGORITHM 불러오기
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# JWT 토큰 생성 함수
def create_access_token(data: dict):
    to_encode = data.copy()
    #expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2PasswordBearer를 사용하여 토큰 추출
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# JWT 토큰 검증 함수
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
