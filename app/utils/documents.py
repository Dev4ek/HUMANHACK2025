import os
import uuid
import aiofiles
from fastapi import UploadFile

async def save_file_to_static(file: UploadFile, destination: str = "static") -> str:
    if not os.path.exists(destination):
        os.makedirs(destination)
    _, ext = os.path.splitext(file.filename)
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(destination, unique_filename)
    
    # Асинхронно записываем содержимое файла на диск
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read() 
        await out_file.write(content)
        
    return "/static/" +  unique_filename