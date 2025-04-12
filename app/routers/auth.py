import datetime
from typing import Optional
from app.dependencies import SessionDep
from app.schemas import auth as auth_schemas
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from app.models import Users               
from app.utils import auth as auth_utils

router_auth = APIRouter(prefix="/auth", tags=["Авторизация"])

@router_auth.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=auth_schemas.AuthOut
)
async def register(
    user: auth_schemas.AuthRegister,
    session: SessionDep
):
    stmt = (
        select(Users)
        .where(Users.email == user.email)
    )
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой email уже существует",
        )

    hashed_password = auth_utils.hash_password(user.password)
    new_user = Users(
        phone=user.phone,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    access_token = auth_utils.create_access_token(data={"sub": str(new_user.id)})

    return auth_schemas.AuthOut(
        access_token=access_token,
        token_type="bearer"
    )
    
@router_auth.post(
    "/login"
)
async def login(
    payload: auth_schemas.AuthLogin,
    session: SessionDep
):
    stmt = (
        select(Users)
        .where(Users.phone == payload.phone)
    )
    result = await session.execute(stmt)
    existing_user = result.scalars().first()
    if not existing_user or not auth_utils.verify_password(
        payload.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
        )

    access_token = auth_utils.create_access_token(data={"sub": str(existing_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}