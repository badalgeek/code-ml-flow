from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide
from starlette.responses import HTMLResponse

from code_ml_flow.containers import Container
from code_ml_flow.daos import GitAccountDAO, GitRepositoryDAO
from code_ml_flow.token_utils import validate_jwt_token
from code_ml_flow.templates.templates import templates

from dependency_injector.providers import Configuration
from fastapi import HTTPException
from github import GithubException, Github

repo_router = APIRouter()

@repo_router.get("/repo/add-new", response_class=HTMLResponse)
@inject
def add(
    request: Request,
    config: Configuration = Depends(Provide[Container.config]),
    git_account_dao: GitAccountDAO = Depends(Provide[Container.git_provider_dao]),
    git_repository_dao: GitRepositoryDAO = Depends(Provide[Container.git_repository_dao]),
):
    user_id= validate_jwt_token(request.cookies.get('access_token'), config)
    
    # Fetch auth token for the user
    git_account = git_account_dao.get_git_account(user_id)
    if not git_account:
        raise HTTPException(status_code=404, detail="No git accountfound for the user")

    # Fetch repositories using PyGithub
    try:
        g = Github(git_account.auth_token)
        git_repositories = g.get_user().get_repos()

        # Fetch repositories from the database
        db_repo_names = {repo.name for repo in git_repository_dao.get_repositories_for_user(user_id)}

        # Compare and mark repositories
        repos_to_display = []
        for repo in git_repositories:
            repos_to_display.append({
                "full_name": repo.full_name,
                "url": repo.html_url,  # Add this line
                "in_db": repo.full_name in db_repo_names
            })

        # Return the fetched repositories as a list
        return templates.TemplateResponse("repo_list.jinja", {"request": request, "repositories": repos_to_display, "git_account_id": git_account.id})
    except GithubException:
        raise HTTPException(status_code=400, detail="Error fetching repositories from GitHub")

@repo_router.get("/repo/add_repo")
@inject
def add_repository_to_db(
    repo_name: str,
    git_account_id: str,
    request: Request,
    config: Configuration = Depends(Provide[Container.config]),
    git_repository_dao: GitRepositoryDAO = Depends(Provide[Container.git_repository_dao]),
):
    user_id = validate_jwt_token(request.cookies.get('access_token'), config)

    try:
        git_repository_dao.add_repository(user_id, repo_name, int(git_account_id))
        return {"status": "success", "message": "Repository added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")