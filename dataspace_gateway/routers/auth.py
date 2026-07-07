from fastapi import APIRouter

from dataspace_gateway.config import settings
from dataspace_gateway.schemas import LoginRequest, LoginResponse
from dataspace_gateway.upstream_client import upstream_request

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and retrieve an access token",
    description=(
        "Exchanges Middleware account credentials for a Bearer access token. "
        "Use the returned accessToken as `Authorization: Bearer <token>` on every "
        "other endpoint in this gateway."
    ),
)
async def login(payload: LoginRequest) -> LoginResponse:
    response = await upstream_request(
        "POST", settings.enpower_base_url, "/api/user/auth", json=payload.model_dump()
    )
    return response.json()
