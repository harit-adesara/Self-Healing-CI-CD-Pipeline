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

    repo_info = payload.get("repository", {})
    owner = repo_info.get("owner", {}).get("login")
    repo_name = repo_info.get("name")

    commit_sha = workflow_run.get("head_sha", "")
    branch = workflow_run.get("head_branch", "")
    workflow_id = workflow_run.get("workflow_id")
    run_id = workflow_run.get("id")

    installation = payload.get("installation")
    if not installation or "id" not in installation:
        return {"status": "error", "message": "Missing installation_id"}

    installation_id = installation["id"]

    try:
        github = get_github_client(installation_id)
        repo = github.get_repo(f"{owner}/{repo_name}")
    except Exception as e:
        return {"status": "error", "message": f"Could not authenticate/resolve repo: {e}"}

    try:
        gh_workflow = repo.get_workflow(workflow_id)
        runs = gh_workflow.get_runs(branch=branch)
        latest_run = runs[0] if runs.totalCount > 0 else None
    except Exception as e:
        return {"status": "error", "message": f"Could not resolve latest run: {e}"}

    if latest_run is None or latest_run.id != run_id:
        print(
            f"Ignoring stale run: webhook run_id={run_id}, "
            f"latest run for {branch} is {latest_run.id if latest_run else None}"
        )
        return {
            "status": "ignored",
            "reason": "stale_run",
            "webhook_run_id": run_id,
            "latest_run_id": latest_run.id if latest_run else None,
        }

    state: Data = {
        "owner": owner,
        "repo": repo_name,
        "installation_id": installation_id,
        "workflow_run_id": run_id,
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
        "messages": [],
    }

    try:
        print("start")
        result = workflow.invoke(state)
        print("end")
        return {"status": "received", "result": result}
    except Exception as e:
        print("❌ Workflow failed:", str(e))
        return {"status": "error", "message": str(e)}