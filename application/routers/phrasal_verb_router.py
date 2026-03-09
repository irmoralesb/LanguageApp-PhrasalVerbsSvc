from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    PhrasalVerbSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.phrasal_verb_schema import (
    PhrasalVerbCreate,
    PhrasalVerbUpdate,
    PhrasalVerbResponse,
)
from domain.entities.phrasal_verb_model import PhrasalVerbModel

router = APIRouter(
    prefix="/api/v1/phrasal-verbs",
    tags=["Phrasal Verbs"],
)


# --- User endpoints (phrasalverbs-user role) ---

@router.get(
    "/catalog",
    response_model=list[PhrasalVerbResponse],
    dependencies=[Depends(require_role("phrasalverbs-user"))],
)
async def get_catalog(
    svc: PhrasalVerbSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
):
    items = await svc.get_catalog(skip=skip, limit=limit)
    return [_to_response(i) for i in items]


@router.get(
    "/{phrasal_verb_id}",
    response_model=PhrasalVerbResponse,
    dependencies=[Depends(require_role("phrasalverbs-user"))],
)
async def get_phrasal_verb(
    phrasal_verb_id: UUID,
    svc: PhrasalVerbSvcDep,
    current_user: CurrentUserDep,
):
    pv = await svc.get_by_id(phrasal_verb_id)
    return _to_response(pv)


@router.post(
    "/custom",
    response_model=PhrasalVerbResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("phrasalverbs-user"))],
)
async def create_custom_verb(
    payload: PhrasalVerbCreate,
    svc: PhrasalVerbSvcDep,
    current_user: CurrentUserDep,
):
    pv = PhrasalVerbModel(
        id=None,
        verb=payload.verb,
        particle=payload.particle,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
    )
    created = await svc.add_custom_verb(current_user.user_id, pv)
    return _to_response(created)


# --- Admin endpoints ---

@router.post(
    "/catalog",
    response_model=PhrasalVerbResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def add_to_catalog(
    payload: PhrasalVerbCreate,
    svc: PhrasalVerbSvcDep,
    current_user: CurrentUserDep,
):
    pv = PhrasalVerbModel(
        id=None,
        verb=payload.verb,
        particle=payload.particle,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
    )
    created = await svc.add_to_catalog(pv)
    return _to_response(created)


@router.put(
    "/catalog/{phrasal_verb_id}",
    response_model=PhrasalVerbResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_catalog_verb(
    phrasal_verb_id: UUID,
    payload: PhrasalVerbUpdate,
    svc: PhrasalVerbSvcDep,
    current_user: CurrentUserDep,
):
    updated = await svc.update_catalog_verb(
        phrasal_verb_id=phrasal_verb_id,
        verb=payload.verb,
        particle=payload.particle,
        definition=payload.definition,
        example_sentence=payload.example_sentence,
    )
    return _to_response(updated)


@router.delete(
    "/catalog/{phrasal_verb_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_catalog_verb(
    phrasal_verb_id: UUID,
    svc: PhrasalVerbSvcDep,
    current_user: CurrentUserDep,
):
    await svc.delete_catalog_verb(phrasal_verb_id)


def _to_response(pv: PhrasalVerbModel) -> PhrasalVerbResponse:
    return PhrasalVerbResponse(
        id=pv.id,
        verb=pv.verb,
        particle=pv.particle,
        definition=pv.definition,
        example_sentence=pv.example_sentence,
        is_catalog=pv.is_catalog,
        created_by_user_id=pv.created_by_user_id,
        created_at=pv.created_at,
    )
