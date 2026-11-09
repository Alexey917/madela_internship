from fastapi import APIRouter, Depends, Header, HTTPException, status, Response 
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.schemas import LoginRequest, TokenResponse, VerifyResponse
from app.security import create_token, decode_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_token(user.id, user.role.value)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.get("/verify", response_model=VerifyResponse)
async def verify(response: Response, authorization: str | None = Header(default=None)):
    """Проверка JWT для Gateway (auth_request)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")


    response.headers["X-User-Id"] = str(payload["sub"])
    response.headers["X-User-Role"] = payload.get("role", "user")
    
    return VerifyResponse(
        valid=True,
        user_id=int(payload["sub"]),
        role=payload.get("role"),
    )