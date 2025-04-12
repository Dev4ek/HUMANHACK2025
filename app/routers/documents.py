import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import SessionDep, UserTokenDep
from app.models import Department, Employee, Document, DocumentRecipient, DocumentSignature
from app.schemas import documents as documents_schemas
from app.models import Employee
from app.models import Document 

router_documents = APIRouter(prefix="/documents", tags=["Документы"])

UPLOAD_DIR = "static"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router_documents.get(
    "",
    response_model=List[documents_schemas.DocumentResponse],
    summary="Получить список документов"
)
async def list_documents(session: SessionDep,Bearer: UserTokenDep):
    stmt = select(Document)
    result = await session.execute(stmt)
    docs = result.scalars().all()
    return docs


@router_documents.get(
    "/{document_id}",
    response_model=documents_schemas.DocumentResponse,
    summary="Получить детали документа по ID",
)
async def get_document(document_id: int, session: SessionDep,current_user: UserTokenDep):
    stmt = select(Document).where(Document.document_id == document_id)
    result = await session.execute(stmt)
    document = result.scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return document


@router_documents.post(
    "/upload",
    response_model=documents_schemas.DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить документ в виде файла"
)
async def upload_document(
    session: SessionDep,
    current_user: UserTokenDep,
    sender_id: int = Form(...),
    title: str = Form(...),
    status: str = Form(...),
    file: UploadFile = File(...),
):
    stmt = select(Employee).where(Employee.employee_id == sender_id)
    result = await session.execute(stmt)
    sender = result.scalars().first()
    if not sender:
        raise HTTPException(status_code=404, detail="Отправитель не найден")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        file_content = await file.read()
        f.write(file_content)
    
    new_doc = Document(
        sender_id=sender_id,
        title=title,
        content=file_path,  
        status=status,
    )
    session.add(new_doc)
    await session.commit()
    await session.refresh(new_doc)
    return new_doc


@router_documents.post(
    "/send",
    status_code=status.HTTP_200_OK,
    summary="Отправить документ получателям"
)
async def send_document(
    payload: documents_schemas.DocumentSend,
    session: SessionDep,
    current_user: UserTokenDep
    ):
    stmt = select(Document).where(Document.document_id == payload.document_id)
    result_doc = await session.execute(stmt)
    doc = result_doc.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    for recipient_id in payload.recipient_ids:
        stmt = select(Employee).where(Employee.employee_id == recipient_id)
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
    return {"message": "Документ отправлен получателям"}


@router_documents.post(
    "/sign",
    status_code=status.HTTP_200_OK,
    summary="Подписать документ"
)
async def sign_document(
    payload: documents_schemas.DocumentSign,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Document).where(Document.document_id == payload.document_id)
    result_doc = await session.execute(stmt)
    doc = result_doc.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    stmt = select(Employee).where(Employee.employee_id == payload.employee_id)
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


@router_documents.get(
    "/incoming",
    response_model=List[documents_schemas.DocumentResponse],
    summary="Получить входящие документы для подписания"
)
async def incoming_documents(
    current_user: UserTokenDep,
    session: SessionDep,
):
    employee_id = current_user.id
    stmt = select(DocumentRecipient).where(
        DocumentRecipient.recipient_id == employee_id,
        DocumentRecipient.status == "sent"
    )
    result = await session.execute(stmt)
    recipient_records = result.scalars().all()

    if not recipient_records:
        return []

    doc_ids = [record.document_id for record in recipient_records]
    stmt_docs = select(Document).where(Document.document_id.in_(doc_ids))
    result_docs = await session.execute(stmt_docs)
    documents = result_docs.scalars().all()
    return documents


@router_documents.get(
    "/history",
    response_model=List[documents_schemas.DocumentResponse],
    summary="Получить историю документов сотрудника"
)
async def document_history(
    current_user: UserTokenDep,
    session: SessionDep,
):
    employee_id = current_user.id
    stmt_created = select(Document).where(Document.sender_id == employee_id)
    result_created = await session.execute(stmt_created)
    created_docs = result_created.scalars().all()

    stmt_signed = select(DocumentSignature).where(DocumentSignature.employee_id == employee_id)
    result_signed = await session.execute(stmt_signed)
    signed_assocs = result_signed.scalars().all()
    signed_doc_ids = {assoc.document_id for assoc in signed_assocs}

    if signed_doc_ids:
        stmt_docsigned = select(Document).where(Document.document_id.in_(signed_doc_ids))
        result_docsigned = await session.execute(stmt_docsigned)
        signed_docs = result_docsigned.scalars().all()
    else:
        signed_docs = []

    all_docs = {doc.document_id: doc for doc in (created_docs + signed_docs)}
    history = list(all_docs.values())
    return history

