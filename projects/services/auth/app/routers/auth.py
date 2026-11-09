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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_token(user.id, user.role.value, user.email)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id, email=user.email)


@router.get("/verify", response_model=VerifyResponse)
async def verify(response: Response, authorization: str | None = Header(default=None)) -> VerifyResponse:
    """
    Проверка JWT для Gateway (auth_request).
    Возвращает 200 + X-User-Id/X-User-Role/X-User-Email в headers,
    либо 401 при невалидном токене.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = int(payload["sub"])
    role = payload.get("role", "user")
    email = payload.get("email", "")

    response.headers["X-User-Id"] = str(user_id)
    response.headers["X-User-Role"] = role
    response.headers["X-User-Email"] = email

    return VerifyResponse(
        valid=True,
        user_id=int(payload["sub"]),
        role=payload.get("role"),
        email=email
    )