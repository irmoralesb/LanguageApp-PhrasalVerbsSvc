from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class UserClaims:
    """
    Represents the authenticated user extracted from JWT token claims.

    The Identity Service issues tokens with roles grouped by service name:
        {"sub": "<user_id>", "email": "...", "roles": {"my-service": ["admin", "user"]}}

    This model replaces the IdentityService's UserWithRolesModel for consumer services
    that only need to read claims without a local user database lookup.
    """
    user_id: UUID
    email: str
    roles: dict[str, list[str]] = field(default_factory=dict)
