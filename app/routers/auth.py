import random
import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.users import Users
from app.dependencies import SessionDep
from app.schemas import auth as auth_schemas
from app.utils import auth as auth_utils


router_auth = APIRouter(prefix="/auth", tags=["Авторизация"])

verification_codes = {}


def send_telegram_code(phone: str, code: int):
    print(f"Ваш код для {phone}: {code}")


@router_auth.post("/request-code")
async def request_code(phone: str, session: SessionDep):
    code = random.randint(1000, 9999)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    verification_codes[phone] = {"code": str(code), "expiry": expiry, "is_verified": False}

    send_telegram_code(phone, code)

    return {"detail": "Код отправлен","code":code}


@router_auth.post("/verify-code")
async def verify_code(phone: str, code: str,session: SessionDep):
    user_db = await Users.get_by_phone(
        session=session,
        phone=phone
    )

    if not user_db:
        stored = verification_codes.get(phone)
        if not stored:
            raise HTTPException(status_code=401, detail="Код не найден")
        if stored['code'] != code:
            raise HTTPException(status_code=401, detail="Неверный код")
        if stored['expiry'] < datetime.datetime.utcnow():
            del verification_codes[phone]
            raise HTTPException(status_code=401, detail="Код устарел")

        stored['is_verified'] = True
        
        return {"detail": "Код подтвержден"}
    else:
        access_token = auth_utils.create_access_token(data={"sub": str(user_db.id)})
        return auth_schemas.AuthOut(access_token=access_token, token_type="bearer")
    


@router_auth.post("/register", response_model=auth_schemas.AuthOut)
async def register(user: auth_schemas.AuthRegister, session: SessionDep):
    stored = verification_codes.get(user.phone)
    if not stored or not stored.get('is_verified'):
        raise HTTPException(status_code=400, detail="Сначала подтвердите код")

    existing_user = await Users.get_by_phone(
        session=session,
        phone=user.phone
        )


    if existing_user:
        raise HTTPException(status_code=400, detail="Такой номер уже существует")

    new_user = await Users.create(
        session=session,
        phone=user.phone,
        first_name=user.first_name,
        last_name=user.last_name,
    )
   

    del verification_codes[user.phone]

    access_token = auth_utils.create_access_token(data={"sub": str(new_user.id)})
    return auth_schemas.AuthOut(access_token=access_token, token_type="bearer")


