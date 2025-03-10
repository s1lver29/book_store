from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllbooks", "UpdateBook"]


class BaseBook(BaseModel):
    title: str
    author: str
    year: int = Field(
        default=2020, le=datetime.now().year, description="Year cannot be in the future"
    )


class IncomingBook(BaseBook):
    pages: int = Field(
        default=150, alias="pages", ge=1, description="Pages must be greater than zero"
    )


class ReturnedBook(BaseBook):
    id: int
    pages: int

    class Config:
        from_attributes = True


class UpdateBook(BaseBook):
    title: str | None = None
    author: str | None = None
    year: int | None = Field(
        None, le=datetime.now().year, description="Year cannot be in the future"
    )
    pages: int | None = Field(None, ge=1, description="Pages must be greater than zero")
    seller_id: int | None = None

    class Config:
        from_attributes = True


class ReturnedAllbooks(BaseModel):
    books: list[ReturnedBook]
