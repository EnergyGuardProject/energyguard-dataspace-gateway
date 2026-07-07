import base64
import json
import time
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(
    description='Paste the accessToken from POST /auth/login (without the word "Bearer").'
)
optional_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_jwt_payload(token: str) -> dict:
    try:
        payload_b64 = token.split(".")[1]
        padding = "=" * (-len(payload_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
    except Exception:
        return {}


def is_token_expired(token: str) -> bool:
    """Reads the JWT's own exp claim locally - no signature verification, no upstream
    round trip needed just to tell the caller their token is stale."""
    exp = _decode_jwt_payload(token).get("exp")
    return exp is not None and time.time() >= exp


def _expired_token_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error_code": "token_expired",
            "message": "Access token has expired - log in again via POST /auth/login.",
        },
    )


async def get_authorization_header(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Passes the caller's own access token straight through to upstream services.

    This gateway does not store or manage sessions - each request must carry the
    token the caller obtained from /auth/login. Using HTTPBearer (instead of a plain
    Header) gives Swagger UI a single "Authorize" button that applies to every
    endpoint, instead of a separate text box to fill in on each one.
    """
    if is_token_expired(credentials.credentials):
        raise _expired_token_error()
    return f"Bearer {credentials.credentials}"


async def get_download_authorization(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer_scheme),
    token: Optional[str] = Query(
        None,
        description=(
            "Access token, as an alternative to the Authorization header. Only accepted "
            "on this download endpoint, so a plain link/<a href> can trigger a download "
            "without needing to attach a custom header."
        ),
    ),
) -> str:
    raw_token = credentials.credentials if credentials else token
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "missing_token",
                "message": "Provide a Bearer token via the Authorization header or a ?token= query parameter.",
            },
        )
    if is_token_expired(raw_token):
        raise _expired_token_error()
    return f"Bearer {raw_token}"
