from fastapi import FastAPI, Request
from function import get_github_client
from graph import workflow
from state import Data

app = FastAPI()

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    action = payload.get("action")

    workflow_run = payload.get("workflow_run", {})
    conclusion = workflow_run.get("conclusion")

    if event != "workflow_run" or action != "completed" or conclusion != "failure":
        return {
            "status": "ignored",
            "reason": f"event={event}, action={action}, conclusion={conclusion}",
        }

    repo = payload.get("repository", {})
    owner = repo.get("owner", {}).get("login")
    repo_name = repo.get("name")

    commit_sha = workflow_run.get("head_sha", "")
    branch = workflow_run.get("head_branch", "")

    installation = payload.get("installation")
    if not installation or "id" not in installation:
        return {"status": "error", "message": "Missing installation_id"}

    installation_id = installation["id"]

    try:
        github = get_github_client(installation_id)
        repo = github.get_repo(f"{owner}/{repo_name}")
        current_head = repo.get_branch(branch).commit.sha
    except Exception as e:
        return {"status": "error", "message": f"Could not resolve branch head: {e}"}

    if commit_sha != current_head:
        print(
            f"Ignoring stale run: webhook reported sha={commit_sha}, "
            f"but {branch} is now at {current_head}"
        )
        return {
            "status": "ignored",
            "reason": "stale_run",
            "webhook_sha": commit_sha,
            "current_branch_head": current_head,
        }

    state: Data = {
        "owner": owner,
        "repo": repo_name,
        "installation_id": installation_id,
        "workflow_run_id": workflow_run.get("id"),
        "workflow_name": workflow_run.get("name", ""),
        "workflow_file": "",
        "branch": branch,
        "commit_sha": commit_sha,
        "error_type": "",
        "fixability": "",
        "reason": "",
        "confidence": 0.0,
        "logs": "",
        "repository_tree": [],
        "file_contents": {},
        "root_cause": None,
        "suggested_changes": None,
        "modified_files": {},
        "branch_name": None,
        "commitMsg": "",
        "commit_sha_new": None,
        "success": False,
        "messages": []
    }

    try:
        print("start")
        result = workflow.invoke(state)
        print("end")
        return {"status": "received", "result": result}
    except Exception as e:
        print("❌ Workflow failed:", str(e))
        return {"status": "error", "message": str(e)}