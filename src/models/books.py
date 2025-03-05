from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

# from src.models import Seller

from .base import BaseModel


class Book(BaseModel):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
