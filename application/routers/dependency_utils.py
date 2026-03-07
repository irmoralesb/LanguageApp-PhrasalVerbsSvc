from typing import Annotated, AsyncIterator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import app_settings
from infrastructure.databases.database import get_monitored_db_session
from infrastructure.repositories.language_repository import LanguageRepository
from infrastructure.repositories.phrasal_verb_repository import PhrasalVerbRepository
from infrastructure.repositories.user_profile_repository import UserProfileRepository
from infrastructure.repositories.exercise_repository import ExerciseRepository
from application.services.token_service import TokenService
from application.services.authorization_service import AuthorizationService
from application.services.phrasal_verb_catalog_service import PhrasalVerbCatalogService
from application.services.user_profile_service import UserProfileService
from application.services.exercise_service import ExerciseService
from domain.entities.token_claims import UserClaims
from domain.exceptions.auth_errors import MissingRoleError
from domain.interfaces.llm_provider import LLMProviderInterface
from infrastructure.observability.security_logger import (
    log_authentication_success,
    log_authentication_failure,
    log_role_check_granted,
    log_role_check_denied,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with get_monitored_db_session() as db:
        yield db


# --- Repository providers ---

def get_language_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> LanguageRepository:
    return LanguageRepository(db)


def get_phrasal_verb_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> PhrasalVerbRepository:
    return PhrasalVerbRepository(db)


def get_user_profile_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> UserProfileRepository:
    return UserProfileRepository(db)


def get_exercise_repository(db: Annotated[AsyncSession, Depends(get_db_session)]) -> ExerciseRepository:
    return ExerciseRepository(db)


# --- LLM provider ---

def get_llm_provider() -> LLMProviderInterface:
    provider_name = app_settings.llm_provider.lower()
    if provider_name == "openai":
        from infrastructure.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(
            api_key=app_settings.llm_api_key,
            model=app_settings.llm_model,
            max_tokens=app_settings.llm_max_tokens,
            temperature=app_settings.llm_temperature,
        )
    elif provider_name == "anthropic":
        from infrastructure.llm.anthropic_provider import AnthropicProvider
        return AnthropicProvider(
            api_key=app_settings.llm_api_key,
            model=app_settings.llm_model,
            max_tokens=app_settings.llm_max_tokens,
            temperature=app_settings.llm_temperature,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")


# --- Service providers ---

def get_phrasal_verb_catalog_service(
    repo: Annotated[PhrasalVerbRepository, Depends(get_phrasal_verb_repository)],
) -> PhrasalVerbCatalogService:
    return PhrasalVerbCatalogService(repo)


def get_user_profile_service(
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
) -> UserProfileService:
    return UserProfileService(profile_repo, language_repo)


def get_exercise_service(
    exercise_repo: Annotated[ExerciseRepository, Depends(get_exercise_repository)],
    pv_repo: Annotated[PhrasalVerbRepository, Depends(get_phrasal_verb_repository)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_user_profile_repository)],
    language_repo: Annotated[LanguageRepository, Depends(get_language_repository)],
    llm: Annotated[LLMProviderInterface, Depends(get_llm_provider)],
) -> ExerciseService:
    return ExerciseService(exercise_repo, pv_repo, profile_repo, language_repo, llm)


def get_token_service() -> TokenService:
    return TokenService(
        app_settings.secret_token_key,
        app_settings.auth_algorithm,
    )


def get_authorization_service() -> AuthorizationService:
    return AuthorizationService()


# --- Authentication ---

oauth_bearer = OAuth2PasswordBearer(tokenUrl=app_settings.token_url)


async def get_authenticated_user(
    token: Annotated[str, Depends(oauth_bearer)],
    token_svc: Annotated[TokenService, Depends(get_token_service)],
) -> UserClaims:
    try:
        claims = token_svc.decode_token(token)
        log_authentication_success(claims.user_id, claims.email)
        return claims
    except Exception:
        log_authentication_failure("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


# --- Authorization dependency factories ---

def require_role(role_name: str):
    async def role_checker(
            current_user: CurrentUserDep,
            authz_svc: AuthzSvcDep,
    ) -> bool:
        try:
            has_role = authz_svc.check_role(current_user, role_name)
            if has_role:
                log_role_check_granted(current_user.user_id, role_name)
                return True
        except MissingRoleError:
            log_role_check_denied(current_user.user_id, role_name)
            raise
        return False
    return role_checker


# --- Clean aliases ---

LanguageRepoDep = Annotated[LanguageRepository, Depends(get_language_repository)]
PhrasalVerbSvcDep = Annotated[PhrasalVerbCatalogService, Depends(get_phrasal_verb_catalog_service)]
UserProfileSvcDep = Annotated[UserProfileService, Depends(get_user_profile_service)]
ExerciseSvcDep = Annotated[ExerciseService, Depends(get_exercise_service)]
TokenSvcDep = Annotated[TokenService, Depends(get_token_service)]
CurrentUserDep = Annotated[UserClaims, Depends(get_authenticated_user)]
AuthzSvcDep = Annotated[AuthorizationService, Depends(get_authorization_service)]
