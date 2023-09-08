from fastapi import FastAPI, Depends, HTTPException
import httpx
from starlette.responses import HTMLResponse, RedirectResponse
import uvicorn

app = FastAPI()

CLIENT_ID = "Iv1.5d125b279ca698ff"
CLIENT_SECRET = "d0c590ba529223d392c4c1fb28545a585263de8e"
REDIRECT_URI = "http://localhost:8000/callback"
AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

@app.get("/", response_class=HTMLResponse)
async def home():
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

@app.get("/login")
def login():
    response = RedirectResponse(url=f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}")
    return response


@app.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            headers={
                "Accept": "application/json"
            },
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI
            }
        )
        data = response.json()

    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Could not get access token")

    # Fetch repositories and commits using the access_token
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"token {access_token}"
        }
        repos_response = await client.get("https://api.github.com/user/repos", headers=headers)
        repos = repos_response.json()
        html_content = "<h2>Repositories and their Commits</h2>"
        for repo in repos:
            repo_name = repo["name"]
            commits_response = await client.get(f"https://api.github.com/repos/{repo['full_name']}/commits", headers=headers)
            commits = commits_response.json()
            html_content += f"<h3>{repo_name}</h3><ul>"
            for commit in commits:
                html_content += f"<li>{commit['commit']['message']} - {commit['commit']['author']['name']}</li>"
            html_content += "</ul>"
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)