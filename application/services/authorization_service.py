from domain.entities.token_claims import UserClaims
from domain.exceptions.auth_errors import MissingRoleError
from core.settings import app_settings


class AuthorizationService:
    """
    Service for handling authorization checks using JWT token claims.

    Roles in the JWT token are grouped by service name:
        {"my-service": ["admin", "user"], "other-service": ["viewer"]}

    This service checks roles for the current service (identified by service_name in settings).
    """

    def __init__(self):
        self.service_name = app_settings.service_name

    def check_role(
        self,
        user: UserClaims,
        role_name: str,
        service_name: str | None = None,
    ) -> bool:
        """
        Check if user has a specific role for a given service.

        Args:
            user: User claims extracted from JWT token
            role_name: Name of role to check
            service_name: Optional service name override. Defaults to current service.

        Returns:
            True if user has the role

        Raises:
            MissingRoleError: If user lacks the required role
        """
        target_service = service_name or self.service_name
        service_roles = user.roles.get(target_service, [])

        if role_name not in service_roles:
            raise MissingRoleError(role_name)

        return True

    def get_user_roles(
        self,
        user: UserClaims,
        service_name: str | None = None,
    ) -> list[str]:
        """
        Get all roles for the user in a given service.

        Args:
            user: User claims extracted from JWT token
            service_name: Optional service name override. Defaults to current service.

        Returns:
            List of role names
        """
        target_service = service_name or self.service_name
        return user.roles.get(target_service, [])
