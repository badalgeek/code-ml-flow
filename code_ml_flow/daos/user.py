from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.orm import Session

from code_ml_flow.models import User
from code_ml_flow.error import UserNotFoundError

class UserDAO:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_user_by_email(self, email: str) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.email_id == email).first()
            return user

    def create_user(self, email: str) -> User:
        with self.session_factory() as session:
            user = User(email_id=email)
            session.add(user)
            session.commit()
            return user.id

    def delete_by_id(self, user_id: int) -> None:
        with self.session_factory() as session:
            entity: User = session.query(User).filter(User.id == user_id).first()
            if not entity:
                raise UserNotFoundError(user_id)
            session.delete(entity)
            session.commit()