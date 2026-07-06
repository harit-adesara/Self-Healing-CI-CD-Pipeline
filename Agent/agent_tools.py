from typing import Annotated
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.tools import tool, InjectedToolCallId
from state import Data
from typing import Literal
from function import get_github_client
from dotenv import load_dotenv

load_dotenv()

@tool
def read_file(
    state: Annotated[Data, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    file_path: str,
):
    """
    Read the complete contents of a repository file.It will read single file from the repository and store it in state["file_contents"].

    Use this tool whenever you need to inspect source code, workflow files,
    configuration files, Dockerfiles, or dependency files before making a change.

    IMPORTANT:
    - Do not guess file contents.
    - Always read the file before modifying it.
    """
    try:
        github = get_github_client(state["installation_id"])
        repo = github.get_repo(f"{state['owner']}/{state['repo']}")
        file = repo.get_contents(file_path, ref=state["commit_sha"])
        content = file.decoded_content.decode("utf-8")
    except Exception as e:
        return f"Error reading '{file_path}': {e}"

    merged = dict(state["file_contents"])
    merged[file_path] = content

    return Command(update={
        "file_contents": merged,
        "messages": [
            {
                "role": "tool",
                "content": f"Read '{file_path}' successfully.",
                "tool_call_id": tool_call_id,
            }
        ],
    })


@tool
def read_multiple_files(
    state: Annotated[Data, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    file_paths: list[str],
):
    """
    Read several repository files in one call.

    Use this tool when diagnosing issues involving multiple files such as
    workflows, Dockerfiles, configuration files, or source code.

    Prefer this tool instead of multiple read_file calls whenever possible.
    """
    github = get_github_client(state["installation_id"])
    repo = github.get_repo(f"{state['owner']}/{state['repo']}")
    merged = dict(state["file_contents"])
    read_ok = []
    for path in file_paths:
        try:
            file = repo.get_contents(path, ref=state["commit_sha"])
            merged[path] = file.decoded_content.decode("utf-8")
            read_ok.append(path)
        except Exception as e:
            print(f"Error reading {path}: {e}")

    return Command(update={
        "file_contents": merged,
        "messages": [
            {
                "role": "tool",
                "content": f"Read files: {read_ok}",
                "tool_call_id": tool_call_id,
            }
        ],
    })


@tool
def search_code(state: Annotated[Data, InjectedState], query: str):
    """
    Search the repository to locate files, imports, classes, functions,
    workflows, configuration, or error-related code.

    Use this tool whenever you do not know which file contains the required information.

    Examples:
    - import
    - FastAPI
    - package.json
    - requirements.txt
    - Dockerfile
    """
    try:
        github = get_github_client(state["installation_id"])
        search_query = f"{query} repo:{state['owner']}/{state['repo']}"
        results = github.search_code(search_query)
        files = [result.path for result in results]
        return f"Found files: {files}"
    except Exception as e:
        return f"Error searching code: {e}"


@tool
def create_file(
    state: Annotated[Data, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    file_path: str,
    content: str,
):
    """
    Create a new repository file only if it does not already exist.

    Before creating dependency files such as:

    - requirements.txt
    - package.json
    - pyproject.toml
    - Pipfile

    you MUST inspect the project's source code using read_file or
    read_multiple_files to determine the actual dependencies.

    Never create dependency files from assumptions.

    Never create empty dependency files.

    Create only files required to resolve the CI/CD failure.
    """
    if file_path in state["file_contents"] or file_path in state["repository_tree"]:
        return f"Error: '{file_path}' already exists. Use update_file instead."

    modified = dict(state["modified_files"])
    modified[file_path] = content

    return Command(update={
        "modified_files": modified,
        "messages": [
            {
                "role": "tool",
                "content": f"Created '{file_path}' and staged it for commit.",
                "tool_call_id": tool_call_id,
            }
        ],
    })


@tool
def update_file(
    state: Annotated[Data, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    file_path: str,
    operation: Literal["replace", "insert_after", "insert_before", "delete"],
    target: str,
    content: str = "",
):
    """
    Modify an existing repository file.

    Only use after reading the file and confirming the required change.

    Make the smallest possible modification that fixes the issue.

    Never overwrite unrelated code.
    """
    if file_path in state["modified_files"]:
        file_content = state["modified_files"][file_path]
    elif file_path in state["file_contents"]:
        file_content = state["file_contents"][file_path]
    else:
        return f"Error: '{file_path}' has not been read yet. Call read_file first, or use create_file if it's a new file."

    try:
        if operation == "replace":
            if target not in file_content:
                return "Error: target text not found."
            updated = file_content.replace(target, content, 1)
        elif operation == "delete":
            if target not in file_content:
                return "Error: target text not found."
            updated = file_content.replace(target, "", 1)
        elif operation == "insert_after":
            if target not in file_content:
                return "Error: target text not found."
            updated = file_content.replace(target, target + "\n" + content, 1)
        elif operation == "insert_before":
            if target not in file_content:
                return "Error: target text not found."
            updated = file_content.replace(target, content + "\n" + target, 1)
        else:
            return "Error: invalid operation."
    except Exception as e:
        return f"Error updating '{file_path}': {e}"

    modified = dict(state["modified_files"])
    modified[file_path] = updated

    return Command(update={
        "modified_files": modified,
        "messages": [
            {
                "role": "tool",
                "content": f"Successfully updated '{file_path}'.",
                "tool_call_id": tool_call_id,
            }
        ],
    })