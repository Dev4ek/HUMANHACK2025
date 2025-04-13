import random
import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models import Employees
from app.dependencies import SessionDep
from app.schemas import auth as auth_schemas
from app.utils import auth as auth_utils
from app.utils import main as main_utils


router_auth = APIRouter(prefix="/auth", tags=["Авторизация"])

verification_codes = {}


@router_auth.post(
    "/request-code",
    summary="Отправить код"
)
async def request_code(
    payload: auth_schemas.AuthLogin,
    session: SessionDep
):
    code = random.randint(1000, 9999)
    expiry = main_utils.get_moscow_time() + datetime.timedelta(minutes=10)
    verification_codes[payload.phone] = {"code": str(code), "expiry": expiry, "is_verified": False}

    return {
        "detail": "Код отправлен",
        "code":code
    }

@router_auth.post("/verify-code")
async def verify_code(phone: str, code: str,session: SessionDep):
    employee_exists = await Employees.get_by_phone(
        session=session,
        phone=phone
    )

    if not employee_exists:
        stored = verification_codes.get(phone)
        if not stored:
            raise HTTPException(status_code=401, detail="Код не найден")
        if stored['code'] != code:
            raise HTTPException(status_code=401, detail="Неверный код")
        if stored['expiry'] < main_utils.get_moscow_time():
            del verification_codes[phone]
            raise HTTPException(status_code=401, detail="Код устарел")

        stored['is_verified'] = True
        
        return {"detail": "Код подтвержден"}
    else:
        access_token = auth_utils.create_access_token(data={"sub": str(employee_exists.id)})
        return auth_schemas.AuthOut(access_token=access_token, token_type="bearer")
    

@router_auth.post(
    "/register",
    response_model=auth_schemas.AuthOut,
    summary="Регистрация"
)
async def register(
    user: auth_schemas.AuthRegister,
    session: SessionDep
):
    stored = verification_codes.get(user.phone)
    
    if not stored or not stored.get('is_verified'):
        raise HTTPException(status_code=400, detail="Сначала подтвердите код")

    existing_user = await Employees.get_by_phone(
        session=session,
        phone=user.phone
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Такой номер уже существует")

    new_employee = Employees(
        phone=user.phone,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    session.add(new_employee)
    await session.commit()
    del verification_codes[user.phone]

    access_token = auth_utils.create_access_token(data={"sub": str(new_employee.id)})
    return auth_schemas.AuthOut(
        access_token=access_token,
        token_type="bearer"
    )


