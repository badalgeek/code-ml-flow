from fastapi import APIRouter, Depends, Request
from starlette.responses import HTMLResponse
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Configuration

from code_ml_flow.token_utils import validate_jwt_token
from code_ml_flow.templates.templates import templates
from code_ml_flow.containers import Container
from code_ml_flow.error import InvalidTokenError
from code_ml_flow.daos import UserDAO, GitRepositoryDAO

homepage_router = APIRouter()

@homepage_router.get("/", response_class=HTMLResponse)
@inject
async def home(request: Request, 
               config: Configuration = Depends(Provide[Container.config]),
               git_repository_dao: GitRepositoryDAO = Depends(Provide[Container.git_repository_dao])):
    try:
        user_id = validate_jwt_token(request.cookies.get('access_token'), config)
        repositories = git_repository_dao.get_repositories_for_user(user_id)
        return templates.TemplateResponse("homepage.jinja", {"request": request, "repositories": repositories})
    except InvalidTokenError as err:
        print(err)
        html_content = """
        <html>
            <head>
                <title>FastAPI</title>
            </head>
            <body>
                <h1>Hello, FastAPI!</h1>
                <p><a href="/login">Login With Github</a></p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)