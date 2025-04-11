import datetime
from typing import List, Optional
from app.dependencies import SessionDep
from app.models import Department, Employee, Document, DocumentRecipient, DocumentSignature
from app.schemas import auth as auth_schemas
import bcrypt
import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings         
from app.database import get_session       
from app.models import Users               
from app.utils import auth as auth_utils
from app.schemas import departments as departments_schemas
from app.schemas import documents as documents_schemas

router_documents = APIRouter(prefix="/documents", tags=["Документы"])

@router_documents.get(
    "", 
    response_model=List[documents_schemas.DocumentResponse]
)
async def list_documents(session: SessionDep):
    stmt = (
        select(Document)
    )
    result = await session.execute(stmt)
    docs = result.scalars().all()
    return docs


@router_documents.post(
    "",
    response_model=documents_schemas.DocumentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_document(
    payload: documents_schemas.DocumentCreate,
    session: SessionDep
):
    stmt = (
        select(Employee)
        .where(Employee.employee_id == payload.sender_id)
    )
    result = await session.execute(stmt)
    sender = result.scalars().first()
    
    if not sender:
        raise HTTPException(status_code=404, detail="Отправитель не найден")
    
    new_doc = Document(
        sender_id=payload.sender_id,
        title=payload.title,
        content=payload.content,
        status=payload.status,
    )
    session.add(new_doc)
    await session.commit()
    await session.refresh(new_doc)
    return new_doc

@router_documents.post(
    "/send",
    status_code=status.HTTP_200_OK
)
async def send_document(
    payload: documents_schemas.DocumentSend,
    session: SessionDep
):
    stmt = (
        select(Document)
        .where(Document.document_id == payload.document_id)
    )
    result_doc = await session.execute(stmt)
    doc = result_doc.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    for recipient_id in payload.recipient_ids:
        stmt = (
            select(Employee)
            .where(Employee.employee_id == recipient_id)
        )
        result_recipient = await session.execute(stmt)
        recipient = result_recipient.scalars().first()
        
        if not recipient:
            raise HTTPException(status_code=404, detail=f"Получатель с айди {recipient_id} не найден")
        
        doc_recipient = DocumentRecipient(
            document_id=payload.document_id,
            recipient_id=recipient_id,
            status="sent"
        )
        session.add(doc_recipient)
        
    await session.commit()
    return {"message": "Документ отправлен получаетелем"}

@router_documents.post(
    "/sign",
    status_code=status.HTTP_200_OK
)
async def sign_document(
    payload: documents_schemas.DocumentSign,
    session: SessionDep
):
    stmt = (
        select(Document)
        .where(Document.document_id == payload.document_id)
    )
    result_doc = await session.execute(stmt)
    doc = result_doc.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    stmt = (
        select(Employee)
        .where(Employee.employee_id == payload.employee_id)
    )
    result_emp = await session.execute(stmt)
    employee = result_emp.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    new_signature = DocumentSignature(
        document_id=payload.document_id,
        employee_id=payload.employee_id,
        signature=payload.signature,
        confirmation_method=payload.confirmation_method
    )
    session.add(new_signature)
    await session.commit()
    return {"message": "Документ успешно подписан"}