from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.utils.log import output_log
from app.config.config import config
from app.auth import authenticate_request
import secrets
import importlib.metadata

__version__ = importlib.metadata.version("Peng-Homelab")
__author__ = importlib.metadata.metadata("Peng-Homelab")["Author-email"]

app = FastAPI(
    title=f"{config.app_name} API",
    root_path="",
    version=__version__,
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST, OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)

@app.get("/")
async def read_root():
    return {
        "message": f"{config.app_name} API",
        "version": __version__,
        "author": __author__,
    }

@app.post("/signup")
async def sign_up(request: Request):
    user = await request.json()
    if user["user_name"] == "":
        raise HTTPException(status_code=422, detail="Empty username")
    if user["password"] == "":
        user["password"] = str(secrets.token_urlsafe(16))
    from app.auth import create_user

    response = create_user(user["user_name"], user["password"], user["admin_password"])
    if not response:
        raise HTTPException(status_code=400, detail="User Creation Failed")
    return response

@app.post("/login")
async def login(request: Request):
    user = await request.json()
    if user["user_name"] == "" or user["password"] == "":
        raise HTTPException(status_code=422, detail="Empty username or password")
    from app.auth import authenticate_user

    user_login = authenticate_user(user["user_name"], user["password"])
    if not user_login:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {
        "user_name": user_login["user_name"],
        "api_token": user_login.get("api_token", ""),
        "token_type": "bearer",
    }

@app.get("/ip")
async def get_ip(request: Request, auth: dict = Depends(authenticate_request)):
    from app.services.ip_update.ip_test import get_dns_result

    record_name = request.query_params.get("record_name", "")
    record = get_dns_result(record_name)
    if not record:
        raise HTTPException(status_code=404, detail="DNS record not found")
    return JSONResponse(
        status_code=200,
        content={
            "name": record["name"],
            "ip": record["content"],
            "type": record["type"],
            "ttl": record["ttl"],
            "proxied": record["proxied"],
        },
        media_type="application/json",
    )

@app.post("/ip")
async def update_ip(request: Request, auth: dict = Depends(authenticate_request)):
    from app.services.ip_update.ip_test import update_dns

    data = await request.json()
    current_ip = data.get("current_ip", "")
    new_ip = data.get("new_ip", "")
    if current_ip == "" or new_ip == "":
        raise HTTPException(status_code=422, detail="Empty current_ip or new_ip")
    update_dns(current_ip, new_ip)
    return JSONResponse(
        status_code=200,
        content={
            "old_ip": current_ip,
            "new_ip": new_ip,
            "message": "DNS record update initiated",
        },
        media_type="application/json",
    )
