from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.routers.dependency_utils import (
    ItemSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.item_schema import ItemCreate, ItemUpdate, ItemResponse
from domain.entities.item_model import ItemModel

router = APIRouter(
    prefix="/items",
    tags=["Items (Sample)"],
)


@router.get("", response_model=list[ItemResponse])
async def get_items(
    item_svc: ItemSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get all items (requires authentication)."""
    items = await item_svc.get_all(skip=skip, limit=limit)
    return [_to_response(item) for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: UUID,
    item_svc: ItemSvcDep,
    current_user: CurrentUserDep,
):
    """Get a single item by ID (requires authentication)."""
    item = await item_svc.get_by_id(item_id)
    return _to_response(item)


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def create_item(
    payload: ItemCreate,
    item_svc: ItemSvcDep,
    current_user: CurrentUserDep,
):
    """Create a new item (requires admin role)."""
    item = ItemModel(
        id=None,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    created = await item_svc.create(item)
    return _to_response(created)


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_item(
    item_id: UUID,
    payload: ItemUpdate,
    item_svc: ItemSvcDep,
    current_user: CurrentUserDep,
):
    """Update an existing item (requires admin role)."""
    updated = await item_svc.update(
        item_id=item_id,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
    )
    return _to_response(updated)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_item(
    item_id: UUID,
    item_svc: ItemSvcDep,
    current_user: CurrentUserDep,
):
    """Delete an item (requires admin role)."""
    await item_svc.delete(item_id)


def _to_response(item: ItemModel) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
