from uuid import UUID

import jwt

from domain.entities.token_claims import UserClaims


class TokenService:
    """
    Decode-only token service for consumer microservices.

    This service verifies and decodes JWT tokens issued by the Identity Service.
    It extracts user identity and roles from token claims without making any
    database calls.
    """

    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def decode_token(self, token: str) -> UserClaims:
        """
        Decode a JWT token and return the user claims.

        Args:
            token: Encoded JWT token string

        Returns:
            UserClaims with user_id, email, and roles extracted from the token

        Raises:
            jwt.ExpiredSignatureError: If the token has expired
            jwt.InvalidTokenError: If the token is invalid
        """
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token is missing 'sub' claim")

        return UserClaims(
            user_id=UUID(user_id),
            email=payload.get("email", ""),
            roles=payload.get("roles", {}),
        )
