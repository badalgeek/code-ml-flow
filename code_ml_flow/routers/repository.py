import json
from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide
from starlette.responses import HTMLResponse, RedirectResponse
from dependency_injector.providers import Configuration
from fastapi import HTTPException
from github import GithubException, Github

from code_ml_flow.containers import Container
from code_ml_flow.daos import GitAccountDAO, GitRepositoryDAO, MetricFileDAO, GitCommitDAO
from code_ml_flow.token_utils import validate_jwt_token
from code_ml_flow.templates.templates import templates

repo_router = APIRouter()

@repo_router.get("/repo/show")
@inject
def add_repository_to_db(
    repo_id: str,
    git_account_id: str,
    request: Request,
    config: Configuration = Depends(Provide[Container.config]),
    git_repository_dao: GitRepositoryDAO = Depends(Provide[Container.git_repository_dao]),
    git_commit_dao: GitCommitDAO = Depends(Provide[Container.git_commit_dao]),
):
    repo = git_repository_dao.get_repository(repo_id)

    # Query the GitRepository table to get the repository object
    commits = git_commit_dao.list_commits(repo_id)

    return templates.TemplateResponse("repository.jinja", {
        "request": request,
        "repository": repo.name,
        "commits": commits,
        "repo_id": repo_id,
        "git_account_id": git_account_id
    })
    

@repo_router.get("/repo/add_repo_list", response_class=HTMLResponse)
@inject
def add(
    request: Request,
    config: Configuration = Depends(Provide[Container.config]),
    git_account_dao: GitAccountDAO = Depends(Provide[Container.git_account_dao]),
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
        return templates.TemplateResponse("add_repo_list.jinja", {"request": request, "repositories": repos_to_display, "git_account_id": git_account.id})
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
        repo_id = git_repository_dao.add_repository(user_id, repo_name, int(git_account_id))
        return RedirectResponse(url=f"/repo/show?git_account_id={git_account_id}&repo_id={repo_id}", status_code=302)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@repo_router.get("/repo/sync")
@inject
def sync(
    repo_id: str,
    git_account_id: str,
    request: Request,
    config: Configuration = Depends(Provide[Container.config]),
    git_account_dao: GitAccountDAO = Depends(Provide[Container.git_account_dao]),
    git_repository_dao: GitRepositoryDAO = Depends(Provide[Container.git_repository_dao]),
    git_commit_dao: GitCommitDAO = Depends(Provide[Container.git_commit_dao]),
    metric_file_dao: MetricFileDAO = Depends(Provide[Container.metric_file_dao]) 
):
    user_id= validate_jwt_token(request.cookies.get('access_token'), config)
    
    # Fetch auth token for the user
    git_account = git_account_dao.get_git_account(user_id)

    # Step 2: Authenticate with GitHub using GithubPy
    github = Github(git_account.auth_token)

    # Fetch auth token for the user
    git_repo = git_repository_dao.get_repository(repo_id)

    # Step 3: Fetch the commits for the given repo_id
    repo = github.get_repo(git_repo.name)
    commits = repo.get_commits()

    last_metric_file_id = None
    for commit in commits.reversed:
        # Check if there's a metrics.json file in the commit
        metrics_file = next((file for file in commit.files if file.filename == "metrics.json"), None)
        if metrics_file is not None:
            # If metrics file is present
            metrics_file_content = repo.get_contents(metrics_file.filename, ref=commit.sha).decoded_content.decode('utf-8')
            metrics_data = json.loads(metrics_file_content)

            # Save the metrics.json content to the metric_files table using DAO
            metric_file_id = metric_file_dao.save_metric_file(commit.sha, repo_id, json.dumps(metrics_data))
            
            # If metrics file not changed. Pick the last metrics. 
            last_metric_file_id = metric_file_id
        else:
            metric_file_id = last_metric_file_id
        
        # Save the commit using DAO
        commit_id = git_commit_dao.save_commit(commit.commit.tree.sha, repo_id, metric_file_id, commit.last_modified)


    return RedirectResponse(url=f"/repo/show?git_account_id={git_account_id}&repo_id={repo_id}", status_code=302)