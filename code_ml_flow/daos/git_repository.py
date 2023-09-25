from contextlib import AbstractContextManager
from typing import Callable, Iterator, List
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from code_ml_flow.models import GitRepository, GitAccount, GitCommit

class GitRepositoryDAO:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def add_repository(self, user_id: int, repo_name: str, git_account_id: int) -> int:
        with self.session_factory() as session:
            new_repo = GitRepository(name=repo_name, git_account_id=git_account_id)
            session.add(new_repo)
            session.commit()
            return new_repo.id

    def get_repositories_for_user(self, user_id: int) -> List[GitRepository]:
        with self.session_factory() as session:
            return session.query(GitRepository).join(GitAccount).filter(GitAccount.user_id == user_id).all()
    
    def get_repository(self, repo_id: str) -> GitRepository:
        with self.session_factory() as session:
            git_repository = session.query(GitRepository).filter_by(id=repo_id).first()
            return git_repository