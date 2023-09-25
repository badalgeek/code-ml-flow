from contextlib import AbstractContextManager
from typing import Callable, Iterator

from sqlalchemy.orm import Session

from code_ml_flow.models import GitAccount

class GitAccountDAO:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def create_git_account(self, user_id: int, provider: str, auth_token: str):
        with self.session_factory() as session:
            git_account = GitAccount(provider=provider, auth_token=auth_token, user_id=user_id)
            session.add(git_account)
            session.commit()
        
    def get_git_account(self, user_id: int) -> GitAccount:
        with self.session_factory() as session:
            git_account = session.query(GitAccount).filter_by(user_id=user_id).first()
            return git_account