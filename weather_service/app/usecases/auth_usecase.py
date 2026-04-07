from app.exceptions.auth_errors import InvalidCredentialsError, UserAlreadyExistsError
from app.models import User
from app.repositories.user_repository import UserRepository
from app.services.security import create_access_token, hash_password, verify_password

class AuthUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register_user(self, email: str, password: str) -> User:
        existing_user = self.user_repository.get_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError()

        hashed_password = hash_password(password)
        return self.user_repository.create(email=email, hashed_password=hashed_password)

    def login_user(self, email: str, password: str) -> str:
        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        return create_access_token(user.id)
