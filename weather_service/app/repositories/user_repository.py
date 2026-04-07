from abc import ABC, abstractmethod

from app.models import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def create(self, email: str, hashed_password: str) -> User:
        pass
