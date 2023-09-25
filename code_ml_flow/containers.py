from dependency_injector import containers, providers

from code_ml_flow.database import Database
from code_ml_flow.daos import UserDAO, GitAccountDAO, GitRepositoryDAO, MetricFileDAO, MetricFileDAO, GitCommitDAO


class Container(containers.DeclarativeContainer):

    # wiring_config = containers.WiringConfiguration(modules=[".routers"])

    config = providers.Configuration(yaml_files=["config.yml"])

    db = providers.Singleton(Database, db_url=config.db.url)

    user_dao = providers.Factory(
        UserDAO,
        session_factory=db.provided.session,
    )

    git_account_dao = providers.Factory(
        GitAccountDAO,
        session_factory=db.provided.session,
    )

    git_repository_dao = providers.Factory(
        GitRepositoryDAO,
        session_factory=db.provided.session,
    )

    metric_file_dao = providers.Factory(
        MetricFileDAO,
        session_factory=db.provided.session,
    )

    git_commit_dao = providers.Factory(
        GitCommitDAO,
        session_factory=db.provided.session,
    )