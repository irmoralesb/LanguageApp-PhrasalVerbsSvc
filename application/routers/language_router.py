from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    LanguageRepoDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.language_schema import LanguageResponse

router = APIRouter(
    prefix="/api/v1/languages",
    tags=["Languages"],
    dependencies=[Depends(require_role("phrasalverbs-user"))],
)


@router.get("", response_model=list[LanguageResponse])
async def list_languages(
    repo: LanguageRepoDep,
    current_user: CurrentUserDep,
):
    langs = await repo.get_all()
    return [_to_response(l) for l in langs]


@router.get("/target", response_model=list[LanguageResponse])
async def list_target_languages(
    repo: LanguageRepoDep,
    current_user: CurrentUserDep,
):
    langs = await repo.get_target_languages()
    return [_to_response(l) for l in langs]


@router.get("/native", response_model=list[LanguageResponse])
async def list_native_languages(
    repo: LanguageRepoDep,
    current_user: CurrentUserDep,
):
    langs = await repo.get_native_languages()
    return [_to_response(l) for l in langs]


def _to_response(lang) -> LanguageResponse:
    return LanguageResponse(
        id=lang.id,
        code=lang.code,
        name=lang.name,
        is_target_language=lang.is_target_language,
        is_native_language=lang.is_native_language,
    )
