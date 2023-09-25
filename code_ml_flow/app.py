from fastapi import FastAPI
import uvicorn

from code_ml_flow.containers import Container
from code_ml_flow.routers.repository import repo_router
from code_ml_flow.routers.auth import auth_router
from code_ml_flow.routers.homepage import homepage_router
import code_ml_flow.routers.repository as repository
import code_ml_flow.routers.auth as auth
import code_ml_flow.routers.homepage as homepage

def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=[repository, auth, homepage])
    app = FastAPI()
    app.container = container
    app.include_router(auth_router)
    app.include_router(repo_router)
    app.include_router(homepage_router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)