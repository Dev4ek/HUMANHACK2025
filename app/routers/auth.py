import random
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from app.models import Users
from app.dependencies import SessionDep
from app.schemas import auth as auth_schemas
from app.utils import auth as auth_utils

router_auth = APIRouter(prefix="/auth", tags=["Авторизация"])

register_codes = {}
login_codes = {}

def send_telegram_code(phone: str, code: int):
    print(f"код {code} для телефона {phone}")

@router_auth.post("/request-register-code")
async def request_register_code(phone: str, session: SessionDep):
    stmt = select(Users).where(Users.phone == phone)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="Такой номер уже зарегистрирован")

    code = random.randint(1000, 9999)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    register_codes[phone] = {'code': str(code), 'expiry': expiry}

    send_telegram_code(phone, code)

    return {"detail": "Код для регистрации отправлен"}

@router_auth.post("/request-login-code")
async def request_login_code(phone: str, session: SessionDep):
    stmt = select(Users).where(Users.phone == phone)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    code = random.randint(1000, 9999)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    login_codes[phone] = {'code': str(code), 'expiry': expiry}

    send_telegram_code(phone, code)

    return {"detail": "Код для входа отправлен"}

@router_auth.post("/verify-register-code", response_model=auth_schemas.AuthOut)
async def verify_register_code(
    phone: str,
    code: str,
    first_name: str,
    last_name: str,
    session: SessionDep
):
    stored = register_codes.get(phone)
    if not stored or stored['code'] != code:
        raise HTTPException(status_code=401, detail="Неверный код")

    if stored['expiry'] < datetime.datetime.utcnow():
        del register_codes[phone]
        raise HTTPException(status_code=401, detail="Код устарел")

    del register_codes[phone]

    user = Users(phone=phone, first_name=first_name, last_name=last_name)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access_token = auth_utils.create_access_token(data={"sub": str(user.id)})
    return auth_schemas.AuthOut(access_token=access_token, token_type="bearer")

@router_auth.post("/verify-login-code", response_model=auth_schemas.AuthOut)
async def verify_login_code(
    phone: str,
    code: str,
    session: SessionDep
):
    stored = login_codes.get(phone)
    if not stored or stored['code'] != code:
        raise HTTPException(status_code=401, detail="Неверный код")

    if stored['expiry'] < datetime.datetime.utcnow():
        del login_codes[phone]
        raise HTTPException(status_code=401, detail="Код устарел")

    del login_codes[phone]

    stmt = select(Users).where(Users.phone == phone)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    access_token = auth_utils.create_access_token(data={"sub": str(user.id)})
    return auth_schemas.AuthOut(access_token=access_token, token_type="bearer")
