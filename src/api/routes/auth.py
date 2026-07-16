"""
Auth Middleware for VOYO API
Validates Supabase JWT tokens on protected routes.
"""

import os
import logging
from typing import Dict, Optional

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Header, status
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Supabase signs auth JWTs with an asymmetric EC P-256 key (ES256); the
# public keys are published at the project's JWKS endpoint. We verify
# against those (no shared HS256 secret needed).
_SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
_JWKS_URL = f"{_SUPABASE_URL}/auth/v1/.well-known/jwks.json"
_jwk_client = PyJWKClient(_JWKS_URL) if _SUPABASE_URL else None
if _SUPABASE_URL:
    logger.info("Verifying Supabase JWTs via JWKS (ES256): %s", _JWKS_URL)
else:
    logger.warning(
        "SUPABASE_URL is not set. "
        "Auth middleware will reject every request. "
        "Set it in .env for production use."
    )


class AuthUser(Dict):
    """
    Lightweight dict subclass representing the authenticated user.

    Keys guaranteed present:
        user_id  – UUID string from Supabase auth.users.id
        email    – user email (may be None for anonymous/phone auth)
        role     – Supabase role claim (usually "authenticated")
    """

    pass


# ─── Public helper ────────────────────────────────────────────────────

def _decode_supabase_jwt(token: str) -> Dict:
    """
    Decode and verify a Supabase-issued JWT (ES256, verified via JWKS).

    We verify:
      • signature against the project's published EC P-256 public key
      • "exp" claim (expiration)
      • "aud" claim == "authenticated" (Supabase convention)

    Returns the full decoded payload dict.
    """
    if not _jwk_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "auth_not_configured",
                "message": "Server auth is not configured (missing SUPABASE_URL).",
            },
        )

    # Resolve the ES256 signing key by the token's "kid" from the JWKS.
    try:
        signing_key = _jwk_client.get_signing_key_from_jwt(token).key
    except Exception as exc:  # malformed token, unknown kid, or JWKS fetch error
        logger.debug("JWT signing-key lookup error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "message": "Token is malformed or has an invalid signature.",
            },
        )

    try:
        payload: Dict = jwt.decode(
            token,
            signing_key,
            algorithms=["ES256"],
            audience="authenticated",
            # Clock-skew tolerance: when the server host clock lags the
            # Supabase auth host by a few seconds, a freshly-issued token's
            # `iat` (issued-at) lands in the future relative to this backend
            # and PyJWT rejects it as ImmatureSignatureError — breaking every
            # authed endpoint (incl. /itinerary/plan) on clock-drifted hosts.
            # 60s leeway is standard practice and covers NTP drift.
            leeway=60,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "token_expired",
                "message": "Token has expired. Please sign in again.",
            },
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_audience",
                "message": "Token audience is invalid.",
            },
        )
    except jwt.DecodeError as exc:
        logger.debug("JWT decode error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_token",
                "message": "Token is malformed or has an invalid signature.",
            },
        )


# ─── FastAPI dependency ───────────────────────────────────────────────

async def get_current_user(
    authorization: str = Header(..., description="Bearer <supabase-jwt>"),
) -> AuthUser:
    """
    FastAPI dependency that extracts & validates the Supabase JWT from the
    Authorization header.

    Usage::

        @router.get("/protected")
        async def handler(user=Depends(get_current_user)):
            user_id = user["user_id"]

    Returns an AuthUser dict with at least ``user_id``, ``email``, and ``role``.
    """
    # ── Strip the "Bearer " prefix ────────────────────────────────────
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_auth_header",
                "message": "Authorization header must follow: Bearer <token>",
            },
        )
    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "missing_token",
                "message": "Bearer token is empty.",
            },
        )

    # ── Decode & verify ───────────────────────────────────────────────
    payload = _decode_supabase_jwt(token)

    # Supabase JWTs always have "sub" (user UUID) and "role".
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "malformed_token",
                "message": "Token is missing the 'sub' claim.",
            },
        )

    user = AuthUser(
        user_id=sub,
        email=payload.get("email"),
        role=payload.get("role"),
        # Pass through raw claims in case downstream code needs them
        _raw=payload,
    )
    return user


# ─── Optional dependency (doesn't 401 on missing token) ───────────────

async def get_optional_user(
    authorization: Optional[str] = Header(None),
) -> Optional[AuthUser]:
    """
    Same as ``get_current_user`` but returns ``None`` instead of raising
    when no token is provided.  Useful for endpoints that behave
    differently for authenticated vs. anonymous users.
    """
    if not authorization:
        return None
    try:
        return await get_current_user(authorization=authorization)
    except HTTPException:
        return None
