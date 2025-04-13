import random
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from typing import List
import datetime
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.dependencies import SessionDep, UserTokenDep
from app.models import Documents, Employees
from app.schemas import documents as documents_schemas
from app.utils import documents as documents_utils
from app.utils import main as main_utils

router_documents = APIRouter(prefix="/documents", tags=["Документы"])

@router_documents.post(
    "",
    response_model=documents_schemas.DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить документ на подписание"
)
async def send_document(
    session: SessionDep,
    current_user: UserTokenDep,
    recipient_id: int = Form(...),
    upload_document: UploadFile = File(...),
):
    recipient = await Employees.get_by_id(session, recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")
    
    file_path = await documents_utils.save_file_to_static(upload_document)
    new_document = Documents(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        status="pending",
        file_path=file_path
    )
    session.add(new_document)
    await session.commit()
    await session.refresh(new_document)
    return new_document


@router_documents.get(
    "/sent",
    response_model=List[documents_schemas.DocumentResponse],
    summary="Получить список отправленных документов"
)
async def get_sent_documents(
    session: SessionDep,
    current_user: UserTokenDep
):
    documents = await Documents.get_by_sender_id(session, current_user.id)
    return documents

@router_documents.get(
    "/received",
    response_model=List[documents_schemas.DocumentResponse],
    summary="Получить список полученных документов"
)
async def get_received_documents(
    session: SessionDep,
    current_user: UserTokenDep
):
    documents = await Documents.get_by_recipient_id(session, current_user.id)
    return documents


@router_documents.get(
    "/{document_id}",
    response_model=documents_schemas.DocumentResponse,
    summary="Получить информацию о документе"
)
async def get_document(
    document_id: int,
    session: SessionDep,
    current_user: UserTokenDep
):
    document = await Documents.get_by_id(session, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if current_user.id not in [document.sender_id, document.recipient_id]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому документу")
    return document



verification_codes = {}
@router_documents.post(
    "/sign/request-code",
    summary="Отправить код на подтверждение подписи"
)
async def request_code(
    payload: documents_schemas.DocumentSignRequestCode,
    current_user: UserTokenDep,
    session: SessionDep
):
    
    ducument = await Documents.get_by_id(session, payload.document_id)
    if ducument.status.value == "Подписан":
        raise HTTPException(status_code=400, detail="Документ уже подписан")
        
    code = random.randint(1000, 9999)
    expire = main_utils.get_moscow_time() + datetime.timedelta(minutes=10)
    verification_codes[current_user.phone] = {"code": code, "expire": expire, "is_verified": False}

    return {
        "detail": "Код на подписание отправлен",
        "code": code
    }

@router_documents.patch(
    "/{document_id}/sign",
    response_model=documents_schemas.DocumentResponse,
    summary="Подписать документ с подтверждением смс кодом"
)
async def sign_document(
    document_id: int,
    payload: documents_schemas.DocumentSign,
    session: SessionDep,
    current_user: UserTokenDep
):
    document = await Documents.get_by_id(session, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    # Подпись может выполнять только получатель
    if document.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на подписание этого документа")
    
    if document.status.value == "Подписан":
        raise HTTPException(status_code=400, detail="Документ уже подписан")
    
    stored = verification_codes.get(current_user.phone)
    if not stored:
        raise HTTPException(status_code=401, detail="Код не найден")
    if stored['code'] != payload.code:
        raise HTTPException(status_code=401, detail="Неверный код")
    if stored['expire'] < main_utils.get_moscow_time():
        del verification_codes[current_user.phone]
        raise HTTPException(status_code=401, detail="Код устарел")
    
    del verification_codes[current_user.phone]
    
    signature_source = f"{document.id}-{payload.code}-{current_user.phone}"
    signature = hashlib.sha256(signature_source.encode()).hexdigest()
    
    document.signature = signature
    document.status = "signed"
    document.signed_at = main_utils.get_moscow_time()
    
    await session.commit()
    await session.refresh(document)
    return document