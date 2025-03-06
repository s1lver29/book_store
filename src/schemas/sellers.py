from pydantic import BaseModel, EmailStr

from src.schemas.books import ReturnedBook

__all__ = ["SellerBase", "SellerCreate", "SellerReturn", "SellerWithBooks"]


class SellerBase(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class SellerCreate(SellerBase):
    password: str


class SellerReturn(SellerBase):
    id: int

    class Config:
        from_attributes = True


class SellerWithBooks(SellerReturn):
    books: list[ReturnedBook]
