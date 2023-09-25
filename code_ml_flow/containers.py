from dependency_injector import containers, providers

from code_ml_flow.database import Database
from code_ml_flow.daos import UserDAO
from code_ml_flow.daos import GitAccountDAO
from code_ml_flow.daos import GitRepositoryDAO


class Container(containers.DeclarativeContainer):

    # wiring_config = containers.WiringConfiguration(modules=[".routers"])

    config = providers.Configuration(yaml_files=["config.yml"])

    db = providers.Singleton(Database, db_url=config.db.url)

    user_dao = providers.Factory(
        UserDAO,
        session_factory=db.provided.session,
    )

    git_provider_dao = providers.Factory(
        GitAccountDAO,
        session_factory=db.provided.session,
    )

    git_repository_dao = providers.Factory(
        GitRepositoryDAO,
        session_factory=db.provided.session,
    )