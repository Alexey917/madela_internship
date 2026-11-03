from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import PaymentRead, PaymentCreate
from app.repository import PaymentRepository
from app.dependencies import get_repo
from app.idempotency import check_idempotency, get_cached_response, store_response

router = APIRouter(prefix="/payments", tags=["payment"])

router.get("/{id}", response_model=PaymentRead)
async def get_payment(
    payment_id: int, 
    repo: PaymentRepository = Depends(get_repo)
) -> PaymentRead | None:
    result = await repo.get(payment_id)

    if result in None:
        return HTTPException(status_code=404, detail="Payment not found")
    return PaymentRead.model_validate(result)
    
    
router.post("", model_response=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    request: Request,
    repo: PaymentRepository = Depends(get_repo)
) -> PaymentRead:
    idem_key = await check_idempotency(request)
    cached = await get_cached_response(idem_key)

    if cached is not None:
        return JSONResponse(status_code=cached["status_code"], content=cached["body"])

    payment = await repo.create_and_charge(data.order_id, data.amount)
    result = PaymentRead.model_validate(payment)
    body = result.model_dump(mode="json")
    await store_response(idem_key, 201, body)
    return result


router.post("/{id}/refund", model_response=PaymentRead)
async def refund_payment(
    payment_id: int,
    request: Request,
    repo: PaymentRepository = Depends(get_repo)
) -> PaymentRead:
    idem_key = await check_idempotency(request)
    cached = await get_cached_response(idem_key)

    if cached is not None:
        return JSONResponse(status_code=cached["status_code"], content=cached["body"])

    payment = await repo.refund(payment_id)
    if payment is None:
        body = {"detail": "Cannot refund: payment not found or not succeeded"}
        await store_response(idem_key, 409, body)
        return JSONResponse(status_code=409, content=body)

    result = PaymentRead.model_validate(payment)
    body = result.model_dump(mode="json")
    await store_response(idem_key, 200, body)
    return result

    

