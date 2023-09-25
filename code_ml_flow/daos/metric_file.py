from contextlib import AbstractContextManager
from typing import Callable, Iterator, List
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from code_ml_flow.models import MetricFile

class MetricFileDAO:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def save_metric_file(self, file_hash: str, repository_id: str, file_data: str, created_at):
        with self.session_factory() as session:
            metric_file = MetricFile(
                file_hash=file_hash,
                repository_id=repository_id,
                file_data=file_data,
                created_at=created_at
            )
            session.add(metric_file)
            session.commit()
            return metric_file.id