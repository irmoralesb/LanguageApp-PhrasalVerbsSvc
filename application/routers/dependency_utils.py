from typing import Annotated, AsyncIterator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import app_settings
from infrastructure.databases.database import get_monitored_db_session
from infrastructure.repositories.item_repository import ItemRepository
from application.services.token_service import TokenService
from application.services.authorization_service import AuthorizationService
from application.services.item_service import ItemService
from domain.entities.token_claims import UserClaims
from domain.exceptions.auth_errors import MissingRoleError


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a monitored async DB session per request."""
    async with get_monitored_db_session() as db:
        yield db


# --- Repository providers ---

def get_item_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ItemRepository:
    """Provide an `ItemRepository` bound to the current DB session."""
    return ItemRepository(db)


# --- Service providers ---

def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    """Provide an `ItemService`."""
    return ItemService(item_repo)


def get_token_service() -> TokenService:
    """Provide a `TokenService` configured with settings."""
    return TokenService(
        app_settings.secret_token_key,
        app_settings.auth_algorithm,
    )


def get_authorization_service() -> AuthorizationService:
    """Provide an `AuthorizationService`."""
    return AuthorizationService()


# --- Authentication ---

oauth_bearer = OAuth2PasswordBearer(tokenUrl=app_settings.token_url)


async def get_authenticated_user(
    token: Annotated[str, Depends(oauth_bearer)],
    token_svc: Annotated[TokenService, Depends(get_token_service)],
) -> UserClaims:
    """Decode the token and return the authenticated user claims."""
    try:
        return token_svc.decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


# --- Authorization dependency factories ---

def require_role(role_name: str):
    """
    Dependency factory to check if current user has specific role.

    Usage in router:
        @router.post("", dependencies=[Depends(require_role("admin"))])
    """
    async def role_checker(
            current_user: CurrentUserDep,
            authz_svc: AuthzSvcDep,
    ) -> bool:
        has_role = authz_svc.check_role(current_user, role_name)

        if has_role:
            return True

        raise MissingRoleError(role_name)
    return role_checker


# --- Clean aliases for router signatures ---

ItemSvcDep = Annotated[ItemService, Depends(get_item_service)]
TokenSvcDep = Annotated[TokenService, Depends(get_token_service)]
CurrentUserDep = Annotated[UserClaims, Depends(get_authenticated_user)]
AuthzSvcDep = Annotated[AuthorizationService, Depends(get_authorization_service)]
