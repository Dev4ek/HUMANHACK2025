import json
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmaker
from app.dependencies import get_current_user_from_token
from app.models import Messages, Employees
from app.utils import messages as messages_utils
from starlette.datastructures import MutableHeaders
from starlette.requests import Request

router_chat = APIRouter(prefix="/chat", tags=["Чат"])
manager = messages_utils.ConnectionManager()

@router_chat.websocket("")
async def chat_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    recipient_id = websocket.query_params.get("employee_id")
    if not token:
        await websocket.close()
        return

    # Получаем пользователя по токену
    async with sessionmaker() as session:
        current_user = await get_current_user_from_token(token, session)
        sender_id = int(current_user.id)

    # Регистрируем соединение под идентификатором отправителя.
    await manager.connect(sender_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message_text = message_data.get("message")
                if not message_text:
                    await websocket.send_text("Неверный формат сообщения, ожидается JSON с message")
                    continue
            except Exception:
                await websocket.send_text("Неверный формат сообщения, ожидается JSON.")
                continue

            async with sessionmaker() as session:
                new_message = Messages(
                    sender_id=sender_id,
                    recipient_id=int(recipient_id),
                    message=message_text
                )
                session.add(new_message)
                await session.commit()
                await session.refresh(new_message)

            await manager.send_personal_message(
                json.dumps({
                    "sender_id": sender_id,
                    "message": message_text
                }),
                int(recipient_id)
            )
    except WebSocketDisconnect:
        manager.disconnect(sender_id)