from dependency_injector import containers, providers

from code_ml_flow.database import Database
from code_ml_flow.daos import UserDAO


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(modules=[".routers"])

    config = providers.Configuration(yaml_files=["config.yml"])

    db = providers.Singleton(Database, db_url=config.db.url)

    user_dao = providers.Factory(
        UserDAO,
    )