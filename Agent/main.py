# from fastapi import FastAPI, Request
# from graph import workflow
# from state import Data 

# app = FastAPI()


# @app.post("/webhook")
# async def github_webhook(request: Request):
#     payload = await request.json()

#     print("🔥 Webhook received")

#     repo = payload.get("repository", {})
#     owner = repo.get("owner", {}).get("login", "")
#     repo_name = repo.get("name", "")

#     workflow_run = payload.get("workflow_run", {})

#     commit_sha = payload.get("after", "")
#     branch = payload.get("ref", "")
#     if branch:
#         branch = branch.replace("refs/heads/", "")

#     installation_id = payload.get("installation", {}).get("id", 0)

#     state: Data = {
#         "owner": owner,
#         "repo": repo_name,
#         "installation_id": installation_id,

#         "workflow_run_id": workflow_run.get("id", 0),
#         "workflow_name": workflow_run.get("name", ""),
#         "workflow_file": "",

#         "branch": branch,
#         "commit_sha": commit_sha,

#         "error_type": "",
#         "fixability": "",
#         "reason": "",
#         "confidence": 0.0,

#         "logs": "",
#         "repository_tree": [],
#         "file_contents": {},

#         "root_cause": None,
#         "suggested_changes": None,

#         "modified_files": {},
#         "branch_name": None,

#         "commitMsg": "",

#         "commit_sha_new": None,
#         "success": False,

#         "messages": []
#     }

#     print("📦 State created:", state)

#     result = workflow.invoke(state)

#     return {
#         "status": "received",
#         "result": result
#     }

from fastapi import FastAPI, Request
from graph import workflow
from state import Data

app = FastAPI()


# @app.post("/webhook")
# async def github_webhook(request: Request):
#     payload = await request.json()

#     print(payload.keys())
#     print("Event:", request.headers.get("X-GitHub-Event"))
#     print("Action:", payload.get("action"))
#     print("Installation:", payload.get("installation"))

#     if request.headers.get("X-GitHub-Event") != "workflow_run":
#         return {"status": "ignored"}

#     print("🔥 Webhook received")

#     repo = payload.get("repository", {})
#     owner = repo.get("owner", {}).get("login")
#     repo_name = repo.get("name")

#     workflow_run = payload.get("workflow_run", {})

#     # ✅ correct for workflow_run event
#     commit_sha = workflow_run.get("head_sha", "")
#     branch = workflow_run.get("head_branch", "")

#     installation = payload.get("installation")
#     if not installation or "id" not in installation:
#         return {"status": "error", "message": "Missing installation_id"}

#     installation_id = installation["id"]

#     state: Data = {
#         "owner": owner,
#         "repo": repo_name,
#         "installation_id": installation_id,

#         "workflow_run_id": workflow_run.get("id"),
#         "workflow_name": workflow_run.get("name", ""),
#         "workflow_file": "",

#         "branch": branch,
#         "commit_sha": commit_sha,

#         "error_type": "",
#         "fixability": "",
#         "reason": "",
#         "confidence": 0.0,

#         "logs": "",
#         "repository_tree": [],
#         "file_contents": {},

#         "root_cause": None,
#         "suggested_changes": None,

#         "modified_files": {},
#         "branch_name": None,

#         "commitMsg": "",
#         "commit_sha_new": None,
#         "success": False,

#         "messages": []
#     }

#     print("📦 State created:", state)

#     try:
#         print("start")
#         result = workflow.invoke(state)
#         print("end")
#         return {"status": "received", "result": result}

#     except Exception as e:
#         print("❌ Workflow failed:", str(e))
#         return {
#             "status": "error",
#             "message": str(e)
#         }

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    action = payload.get("action")

    print(payload.keys())
    print("Event:", event)
    print("Action:", action)
    print("Installation:", payload.get("installation"))

    # Only process completed workflow_run events
    if event != "workflow_run" or action != "completed":
        return {"status": "ignored", "reason": f"event={event}, action={action}"}

    print("🔥 Webhook received")

    repo = payload.get("repository", {})
    owner = repo.get("owner", {}).get("login")
    repo_name = repo.get("name")

    workflow_run = payload.get("workflow_run", {})
    commit_sha = workflow_run.get("head_sha", "")
    branch = workflow_run.get("head_branch", "")

    installation = payload.get("installation")
    if not installation or "id" not in installation:
        return {"status": "error", "message": "Missing installation_id"}

    installation_id = installation["id"]

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

    print("📦 State created:", state)

    try:
        print("start")
        result = workflow.invoke(state)
        print("end")
        return {"status": "received", "result": result}
    except Exception as e:
        print("❌ Workflow failed:", str(e))
        return {"status": "error", "message": str(e)}