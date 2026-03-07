class UnauthorizedUserError(Exception):
    """Raised when a user is not authorized to perform an action"""

    def __init__(self, message: str = "User is not authorized to perform this action"):
        self.message = message
        super().__init__(self.message)


class MissingRoleError(Exception):
    """Raised when a user doesn't have required role"""

    def __init__(self, role_name: str):
        self.role_name = role_name
        super().__init__(f"User does not have required role: '{role_name}'")


class MissingPermissionError(Exception):
    """Raised when a user doesn't have required permission"""

    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action
        super().__init__(
            f"User does not have permission to {action} {resource}")
