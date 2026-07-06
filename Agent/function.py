import os
import uuid
import io
import zipfile
import requests
from state import Data,ErrorClassification,CommitMessage
from langchain_openai import ChatOpenAI
from github import Github
from github.Auth import AppAuth
from github import InputGitTreeElement
from dotenv import load_dotenv
from langsmith import traceable
    
load_dotenv()

model=ChatOpenAI(
    api_key=os.getenv("CEREBRAS_API_KEY"),
    model="gpt-oss-120b",
    base_url="https://api.cerebras.ai/v1"
)

def get_github_client(installation_id: int):
    APP_ID = os.getenv("GITHUB_APP_ID")

    PRIVATE_KEY=os.getenv("GITHUB_PRIVATE_KEY_PATH")

    auth = AppAuth(APP_ID, PRIVATE_KEY)
    installation_auth = auth.get_installation_auth(installation_id)

    return Github(auth=installation_auth)

@traceable(name="fetch tree")
def fetch_tree(state: Data):
    """
    Fetch all file paths in the repository.
    """

    github = get_github_client(state["installation_id"])

    repo = github.get_repo(f"{state['owner']}/{state['repo']}")

    tree = repo.get_git_tree(repo.default_branch, recursive=True)

    repository_tree = [
        item.path
        for item in tree.tree
        if item.type == "blob"
    ]

    print("tree fetch")

    return {
        "repository_tree": repository_tree
    }

@traceable(name="create branch")
def create_branch(state: Data):
    """
    Create a new branch from the current commit.
    """

    github = get_github_client(state["installation_id"])
    branch_name = f"AI_FIX-{uuid.uuid4().hex[:8]}"
    repo = github.get_repo(f"{state['owner']}/{state['repo']}")

    repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=state["commit_sha"]
    )

    print("create branch")

    return {
        "branch_name": branch_name
    }

@traceable(name="download logs")
def download_workflow_logs(state: Data):
    """
    Download and extract GitHub Actions workflow logs.
    """

    github = get_github_client(state["installation_id"])

    token = github._Github__requester.auth.token

    url = (
        f"https://api.github.com/repos/"
        f"{state['owner']}/{state['repo']}"
        f"/actions/runs/{state['workflow_run_id']}/logs"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    logs = ""

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for name in zip_file.namelist():
            if name.endswith(".txt"):
                logs += f"\n\n===== {name} =====\n"
                logs += zip_file.read(name).decode("utf-8", errors="ignore")

    print("download logs")

    return {
        "logs": logs
    }

@traceable(name="check branch")
def check_branch(state):
    """
    Prevent infinite self-healing loops.

    If the workflow is already running on an AI-generated fix branch,
    stop the pipeline.
    """

    branch = state["branch"].strip()

    print("check branch")

    if branch.startswith("AI_FIX"):
        state["success"] = False
        state["root_cause"] = (
            f"Workflow is running on AI-generated branch '{branch}'. "
            "Skipping automatic repair to avoid recursive fix attempts."
        )
        return "suggest"

    return "logs"

@traceable(name="classify error")
def classify_error(state:Data):
    """
    CI/CD error classification node
    """

    prompt = f"""
You are an expert CI/CD failure analysis agent.

Analyze the GitHub Actions logs and determine whether the failure can be fixed automatically.

Return exactly one value for fixability:

1. auto
The issue can likely be fixed by modifying files in the repository, such as:
- Source code
- Workflow YAML
- Dockerfile
- package.json
- requirements.txt
- Build scripts
- Configuration files

Examples:
- Dependency installation failures
- Syntax errors
- Test failures
- Build failures
- Workflow YAML mistakes
- Missing imports
- Incorrect versions

2. manual
The issue requires human intervention and cannot be fixed by editing repository files.

Examples:
- Missing GitHub Secrets
- Invalid cloud credentials
- Permission denied
- Repository settings
- Branch protection
- External service outage
- Network failures
- Expired tokens

3. unknown
There is not enough information in the logs to determine whether the issue is automatically fixable.

Also provide:
- confidence (0-100)
- reason 

Workflow Logs:
{state["logs"]}

Repository Tree:
{state["repository_tree"]}

Return only the structured output.
"""

    structure_output=model.with_structured_output(ErrorClassification)
    result=structure_output.invoke(prompt)
    data=result.model_dump()

    print("classify error")

    return {
        "error_type":data["error_type"],
        "fixability":data["fixability"],
        "confidence":data["confidence"],
        "reason":data["reason"]
    }

@traceable(name="divide flow")
def divide_flow_based_on_fixability(state:Data):

    print("divide flow")

    if state["fixability"]=="auto":
        return 'solve'
    else:
        return "suggest"

@traceable(name="suggest fix")
def suggestFix(state:Data):
    prompt = f"For this error {state['reason']} suggest fix how to solve this"

    result=model.invoke(prompt).content

    print("suggest fix")
    return {
        "suggested_changes":result
    }

def sendEmail():
    return

@traceable(name="commit")
def commit(state: Data):
    """
    Commit all staged file modifications to the AI_FIX branch.
    """

    if not state["modified_files"]:
        print("commit skipped: no modified files")
        return {
            "success": False,
            "reason": "No modified files to commit."
        }

    github = get_github_client(state["installation_id"])

    repo = github.get_repo(
        f"{state['owner']}/{state['repo']}"
    )

    # Get AI_FIX branch reference
    ref = repo.get_git_ref(
        f"heads/{state['branch_name']}"
    )

    # Latest commit on AI_FIX branch
    latest_commit = repo.get_git_commit(ref.object.sha)

    # Base tree
    base_tree = repo.get_git_tree(latest_commit.tree.sha)

    tree_elements = []

    for path, content in state["modified_files"].items():
        tree_elements.append(
            InputGitTreeElement(
                path=path,
                mode="100644",
                type="blob",
                content=content,
            )
        )

    # Create new tree
    new_tree = repo.create_git_tree(
        tree=tree_elements,
        base_tree=base_tree,
    )

    # Create commit
    new_commit = repo.create_git_commit(
        message=state["commitMsg"] or "AI: Fix CI/CD pipeline",
        tree=new_tree,
        parents=[latest_commit],
    )

    # Move AI_FIX branch to new commit
    ref.edit(new_commit.sha)

    print("commit")

    return {
        "commit_sha_new": new_commit.sha,
        "success": True,
    }

def successMail():
    return

@traceable(name="commit message")
def commitMsg(state:Data):

    structured_llm = model.with_structured_output(CommitMessage)

    prompt=f"""
    A CI/CD pipeline failure has been fixed.

    Root Cause:
    {state["root_cause"]}

    Original Error:
    {state["reason"]}

    Files Modified:
    {list(state["modified_files"].keys())}

    Generate a concise Git commit message.

    Rules:
    - Maximum 72 characters.
    - Use imperative mood.
    - Describe the actual change.
    - Do not mention AI.
    - Do not include quotes.
    """

    result = structured_llm.invoke(prompt)
    data=result.model_dump()

    print("commitMsg")

    return {
    "commitMsg": data["commit_message"]
    }
