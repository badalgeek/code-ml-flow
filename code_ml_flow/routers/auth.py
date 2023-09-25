import httpx
from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from starlette.responses import HTMLResponse, RedirectResponse
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Configuration

from code_ml_flow.token_utils import create_jwt_token

from code_ml_flow.containers import Container
from code_ml_flow.daos import UserDAO, GitAccountDAO

from github import Github

auth_router = APIRouter()

AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

@auth_router.get("/login")
@inject
def login(config: Configuration = Depends(Provide[Container.config])):
    response = RedirectResponse(url=f"{AUTH_URL}?client_id={config['github']['client_id']}&redirect_uri={config['github']['redirect_url']}", status_code=302)
    return response


@auth_router.get("/callback")
@inject
async def callback(code: str,
                   config: Configuration = Depends(Provide[Container.config]), 
                   user_dao: UserDAO = Depends(Provide[Container.user_dao]),
                   git_account_dao: GitAccountDAO = Depends(Provide[Container.git_provider_dao])):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_URL,
            headers={
                "Accept": "application/json"
            },
            data={
                "client_id": config['github']['client_id'],
                "client_secret": config['github']['client_secret'],
                "code": code,
                "redirect_uri": config['github']['redirect_url']
            }
        )
        data = token_response.json()

    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Could not get access token")

    # Use PyGithub to fetch user's email
    g = Github(access_token)
    user = g.get_user()
    primary_email = next((email.email for email in user.get_emails() if email.primary), None)

    if not primary_email:
        raise HTTPException(status_code=400, detail="Could not fetch user email from GitHub")

    # Check if user exists in the database
    user = user_dao.get_user_by_email(primary_email)
    if not user:
        # Create a new user and add an entry in the git_accounts table
        user_id = user_dao.create_user(primary_email)
        git_account_dao.create_git_account(user_id, "github", access_token)
    else:
        user_id = user.id

    # Create JWT token using jose
    token = create_jwt_token(user_id, config)
    print(token)

    response = RedirectResponse(url=f"/", status_code=302)
    # Set JWT token as a cookie
    response.set_cookie(key="access_token", value=token)  # 1 hour expiry

    # Add more code here, like redirecting the user to a dashboard or homepage
    return response

    # Fetch repositories and commits using the access_token
    # async with httpx.AsyncClient() as client:
    #     headers = {
    #         "Authorization": f"token {access_token}"
    #     }
    #     repos_response = await client.get("https://api.github.com/user/repos", headers=headers)
    #     repos = repos_response.json()
    #     html_content = "<h2>Repositories and their Commits</h2>"
    #     for repo in repos:
    #         repo_name = repo["name"]
    #         commits_response = await client.get(f"https://api.github.com/repos/{repo['full_name']}/commits", headers=headers)
    #         commits = commits_response.json()
    #         html_content += f"<h3>{repo_name}</h3><ul>"
    #         for commit in commits:
    #             html_content += f"<li>{commit['commit']['message']} - {commit['commit']['author']['name']}</li>"
    #         html_content += "</ul>"
    # return HTMLResponse(content=html_content)