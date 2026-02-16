"""
Common response schemas
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """Standard success response"""
    data: T


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response"""
    data: List[T]
    meta: PaginationMeta


class ErrorDetail(BaseModel):
    """Error detail"""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: dict


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str

