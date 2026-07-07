from typing import Any, Optional

import httpx
from fastapi import HTTPException

from dataspace_gateway.config import settings


def _safe_error_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


async def upstream_request(
    method: str,
    base_url: str,
    path: str,
    authorization: Optional[str] = None,
    json: Optional[dict] = None,
    params: Optional[dict] = None,
) -> httpx.Response:
    """Forwards a request to an upstream Data Space service and surfaces its errors.

    Upstream error responses (>=400) are re-raised as HTTPException with the same
    status code and body, so failures from enpower.eurodyn.com or the True Connector
    local API are transparent to the gateway's caller instead of being masked as 500s.
    """
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if authorization:
        headers["Authorization"] = authorization

    async with httpx.AsyncClient(base_url=base_url, timeout=settings.request_timeout) as client:
        try:
            response = await client.request(method, path, headers=headers, json=json, params=params)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Upstream request to {base_url}{path} failed: {exc}") from exc

    if response.status_code == 401 and authorization:
        # Distinguishes "upstream rejected this token" from a locally-detected expiry
        # (see app.dependencies.is_token_expired) so callers can reliably decide to
        # prompt re-login instead of guessing from message text.
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "invalid_token",
                "message": "Upstream rejected this token - log in again via POST /auth/login.",
                "upstream_detail": _safe_error_body(response),
            },
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=_safe_error_body(response))

    return response
