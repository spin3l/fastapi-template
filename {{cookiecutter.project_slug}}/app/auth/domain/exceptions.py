class AuthError(Exception):
    message = "Authentication error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)


class EmailAlreadyRegisteredError(AuthError):
    message = "Email is already registered"


class InvalidCredentialsError(AuthError):
    message = "Incorrect email or password"


class InvalidTokenError(AuthError):
    message = "Invalid or expired token"


class InactiveUserError(AuthError):
    message = "User is inactive"


class UnverifiedEmailError(AuthError):
    message = "Identity provider email is not verified"


class InvalidOAuthStateError(AuthError):
    message = "Invalid OAuth state"


class ForbiddenError(AuthError):
    message = "Not enough permissions"


class UserNotFoundError(AuthError):
    message = "User not found"


class CannotChangeOwnRoleError(AuthError):
    message = "You can't change your own role"


class InvalidGrantError(AuthError):
    message = "Only user admins can be granted resources"


class IdentityProviderError(AuthError):
    message = "Could not authenticate with the identity provider"
