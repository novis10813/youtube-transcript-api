from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List

T = TypeVar("T")

class BaseResponse(BaseModel):
    """基礎回應模型"""
    success: bool = Field(..., description="是否成功")
    error: Optional[str] = Field(None, description="錯誤訊息")
