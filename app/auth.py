from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from passlib.context import CryptContext
from app.utils.log import output_log
from app.utils.minio_connection import MinioStorage
from app.config.config import config
from fastapi import HTTPException, Request
import jwt
import pandas as pd
import os

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    try:
        minio = MinioStorage()
        minio.file_download(f"{config.s3_base_path}/user.xlsx", "user.xlsx")
        user_records = pd.read_excel("user.xlsx").to_dict(orient="records")
        os.remove("user.xlsx")
        user = next((user for user in user_records if user["user_name"] == username), [])
        if not user or len(user) == 0:
            output_log(f"User not found: {username}", "warning")
            return None
        
        if verify_password(password, user["password"]):
            api_key = create_access_token({"sub": username}, expiration_days=7)
            return {
                "user_name": username,
                "api_token": api_key,
            }
        output_log(f"Invalid password for user: {username}", "warning")
        return None
    except Exception as e:
        output_log(f"Authentication error: {str(e)}", "error")
        return None


def create_user(user_name: str, password: str, admin_password: str) -> Optional[Dict]:
    try:
        if not admin_password == config.admin_password:
            output_log("Admin password is incorrect", "error")
            raise HTTPException(status_code=403, detail="Admin password is incorrect")
        minio = MinioStorage()
        minio.file_download(f"{config.s3_base_path}/user.xlsx", "user.xlsx")
        user_records = pd.read_excel("user.xlsx").to_dict(orient="records")
        user = next((user for user in user_records if user["user_name"] == user_name), [])
        if user and len(user) > 0:
            output_log(f"User already exists: {user_name}", "warning")
            raise HTTPException(status_code=400, detail="User already exists")
        hashed_password = get_password_hash(password)
        api_token = create_access_token({"sub": user_name}, None)
        user_records.append({
            "user_name": user_name,
            "password": hashed_password,
        })
        df = pd.DataFrame(user_records)
        df.to_excel("user.xlsx", index=False)
        minio.file_upload("user.xlsx", f"{config.s3_base_path}/user.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return {
            "user_name": user_name,
            "password": hashed_password,
            "api_token": api_token,
        }
    except Exception as e:
        output_log(f"User creation error: {str(e)}", "error")
        return None

def create_access_token(data: dict, expiration_days: int) -> str:
    to_encode = data.copy()
    if expiration_days:
        # Other JWT token has expiration
        expire = datetime.now(timezone.utc) + timedelta(days=expiration_days)
        to_encode.update({"exp": expire})
    else:
        # API token has infinite expiration
        to_encode.update({"exp": datetime.max})
    encoded_jwt = jwt.encode(to_encode, config.jwt_secret_key, algorithm="HS256")
    return encoded_jwt


async def authenticate_request(request: Request):
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Invalid authentication Token")
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        expiration = payload.get("exp")
        # If expiration is None, it means the token is infinite
        # If expiration is not None, check if it is expired with current time
        if expiration and datetime.fromtimestamp(
            expiration, tz=timezone.utc
        ) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token has expired")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid username")
        return {"auth_type": "jwt", "username": username}
    except Exception as e:
        output_log(f"Authentication error: {str(e)}", "error")
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )