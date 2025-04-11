import asyncio
import base64
from fastapi import UploadFile, File, HTTPException
import pytz
from datetime import datetime
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
import os
from uuid import uuid4
import re
from io import BytesIO


def get_moscow_time() -> datetime:
    """Возвращает текущее московское время."""
    
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)
    
    return moscow_time
