import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum, func, DateTime
from datetime import datetime
from app.db import Base


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        default=UserRole.USER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )