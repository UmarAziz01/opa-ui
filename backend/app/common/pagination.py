from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams:
    """Dependency query parameters untuk pagination di endpoint FastAPI."""

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
    ):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), 100)  # Max limit 100 per halaman
        self.offset = (self.page - 1) * self.page_size


class PageMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta

    @classmethod
    def create(cls, items: List[T], total_items: int, params: PaginationParams) -> "PaginatedResponse[T]":
        total_pages = (total_items + params.page_size - 1) // params.page_size if total_items > 0 else 1
        return cls(
            items=items,
            meta=PageMeta(
                page=params.page,
                page_size=params.page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=params.page < total_pages,
                has_prev=params.page > 1,
            ),
        )