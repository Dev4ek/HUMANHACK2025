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

verification_codes = {}

def send_telegram_code(phone: str, code: int):
    print(f"код {code} для телефона {phone}")

@router_auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=auth_schemas.AuthOut
)
async def register(
    user: auth_schemas.AuthRegister,  
    session: SessionDep
):
    stmt = select(Users).where(Users.phone == user.phone)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой номер уже существует",
        )

    new_user = Users(
        phone=user.phone,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    code = random.randint(1000, 9999)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    verification_codes[new_user.phone] = {'code': str(code), 'expiry': expiry}
    send_telegram_code(new_user.phone, code)
    return {"detail": "Код отправлен через Telegram-бот"}

@router_auth.post("/request-code")
async def request_code(
    phone: str,
    session: SessionDep
):

    stmt = select(Users).where(Users.phone == phone)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Пользователь с таким номером не найден"
         )

    code = random.randint(1000, 9999)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    verification_codes[phone] = {'code': str(code), 'expiry': expiry}
    
    send_telegram_code(phone, code)
    
    return {"detail": "Код отправлен через Telegram-бот"}

@router_auth.post("/verify-code")
async def verify_code(
    phone: str,
    code: str,
    session: SessionDep
):

    stored = verification_codes.get(phone)
    if not stored:
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Код не найден. Сначала запросите код."
         )
    if stored['code'] != code:
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Неверный код"
         )
    if stored['expiry'] < datetime.datetime.utcnow():
         del verification_codes[phone]
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Код устарел. Повторите запрос"
         )

    del verification_codes[phone]

    stmt = select(Users).where(Users.phone == phone)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="Пользователь не найден"
         )

    access_token = auth_utils.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
