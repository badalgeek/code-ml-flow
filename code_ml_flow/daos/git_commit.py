from contextlib import AbstractContextManager
from typing import Callable, Iterator, List
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from typing import Tuple
from code_ml_flow.models import GitCommit, MetricFile

class GitCommitDAO:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def save_commit(self, branch_name: str, repository_id: str, metric_file_id, created_at) -> int:
        with self.session_factory() as session:
            git_commit = GitCommit(
                branch_name=branch_name,
                repository_id=repository_id,
                metric_file_id=metric_file_id,
                created_at=created_at
            )
            session.add(git_commit)
            session.commit()
            return git_commit.id
        
    def list_commits(self, repository_id: int) -> List[Tuple[GitCommit, MetricFile]]:
        with self.session_factory() as session:
            # Join GitCommit and MetricFile tables on the commit_id and order by GitCommit's created_at in descending order
            results = (
                session.query(GitCommit, MetricFile)
                .join(MetricFile, GitCommit.metric_file_id == MetricFile.id)
                .filter(GitCommit.repository_id == repository_id)
                .order_by(GitCommit.created_at.desc())
                .all()
            )
            return results