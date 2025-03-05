from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from .base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    e_mail: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    books: Mapped[list["Book"]] = relationship(  # type: ignore  # noqa: F821
        "Book", back_populates="seller", cascade="all, delete-orphan"
    )
