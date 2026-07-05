# # # # from state import Data
# # # # from langchain_core.tools import tool
# # # # from typing import Literal
# # # # from function import get_github_client
# # # # from dotenv import load_dotenv

# # # # load_dotenv()

# # # # @tool
# # # # def read_file(state: Data, file_path: str):
# # # #     """Read single file from the repository
# # # #     """

# # # #     github = get_github_client(state["installation_id"])

# # # #     repo = github.get_repo(f"{state['owner']}/{state['repo']}")

# # # #     file = repo.get_contents(
# # # #         file_path,
# # # #         ref=state["commit_sha"]
# # # #     )

# # # #     return {
# # # #         file_path: file.decoded_content.decode("utf-8")
# # # #     }

# # # # @tool
# # # # def read_multiple_files(state: Data, file_paths: list[str]):
# # # #     """Read multiple files from repository
# # # #     """

# # # #     github = get_github_client(state["installation_id"])

# # # #     repo = github.get_repo(f"{state['owner']}/{state['repo']}")

# # # #     file_contents = {}

# # # #     for path in file_paths:
# # # #         try:
# # # #             file = repo.get_contents(
# # # #                 path,
# # # #                 ref=state["commit_sha"]
# # # #             )

# # # #             file_contents[path] = file.decoded_content.decode("utf-8")

# # # #         except Exception as e:
# # # #             print(f"Error reading {path}: {e}")

# # # #     return {
# # # #         "file_contents": file_contents
# # # #     }

# # # # @tool
# # # # def search_code(state: Data, query: str):


# # # #     """
# # # #     Search for code in the repository.
# # # #     """

# # # #     github = get_github_client(state["installation_id"])

# # # #     search_query = f"{query} repo:{state['owner']}/{state['repo']}"

# # # #     results = github.search_code(search_query)

# # # #     files = []

# # # #     for result in results:
# # # #         files.append(result.path)

# # # #     return {
# # # #         "search_results": files
# # # #     }

# # # # @tool
# # # # def update_file(
# # # #     state,
# # # #     file_path: str,
# # # #     operation: Literal[
# # # #         "replace",
# # # #         "insert_after",
# # # #         "insert_before",
# # # #         "delete"
# # # #     ],
# # # #     target: str,
# # # #     content: str = "",
# # # # ) -> str:
# # # #     """
# # # #     Stage changes to a repository file.

# # # #     Operations:
# # # #     - replace
# # # #     - delete
# # # #     - insert_after
# # # #     - insert_before

# # # #     The change is stored in state["modified_files"].
# # # #     No commit is created.
# # # #     """

# # # #     # Already modified?
# # # #     if file_path in state["modified_files"]:
# # # #         file_content = state["modified_files"][file_path]

# # # #     # Original file
# # # #     elif file_path in state["file_contents"]:
# # # #         file_content = state["file_contents"][file_path]

# # # #     else:
# # # #         return f"Error: '{file_path}' does not exist."

# # # #     # ---------- Apply operation ----------

# # # #     if operation == "replace":

# # # #         if target not in file_content:
# # # #             return f"Error: target text not found."

# # # #         updated = file_content.replace(
# # # #             target,
# # # #             content,
# # # #             1
# # # #         )

# # # #     elif operation == "delete":

# # # #         if target not in file_content:
# # # #             return f"Error: target text not found."

# # # #         updated = file_content.replace(
# # # #             target,
# # # #             "",
# # # #             1
# # # #         )

# # # #     elif operation == "insert_after":

# # # #         if target not in file_content:
# # # #             return f"Error: target text not found."

# # # #         updated = file_content.replace(
# # # #             target,
# # # #             target + "\n" + content,
# # # #             1
# # # #         )

# # # #     elif operation == "insert_before":

# # # #         if target not in file_content:
# # # #             return f"Error: target text not found."

# # # #         updated = file_content.replace(
# # # #             target,
# # # #             content + "\n" + target,
# # # #             1
# # # #         )

# # # #     else:
# # # #         return "Error: invalid operation."

# # # #     # Stage file
# # # #     state["modified_files"][file_path] = updated

# # # #     return f"Successfully updated '{file_path}'."
# # # from typing import Annotated
# # # from langgraph.prebuilt import InjectedState
# # # from state import Data
# # # from langchain_core.tools import tool
# # # from typing import Literal
# # # from function import get_github_client
# # # from dotenv import load_dotenv

# # # load_dotenv()

# # # @tool
# # # def read_file(state: Annotated[Data, InjectedState], file_path: str):
# # #     """Read single file from the repository"""
# # #     github = get_github_client(state["installation_id"])
# # #     repo = github.get_repo(f"{state['owner']}/{state['repo']}")
# # #     file = repo.get_contents(file_path, ref=state["commit_sha"])
# # #     return {file_path: file.decoded_content.decode("utf-8")}


# # # @tool
# # # def read_multiple_files(state: Annotated[Data, InjectedState], file_paths: list[str]):
# # #     """Read multiple files from repository"""
# # #     github = get_github_client(state["installation_id"])
# # #     repo = github.get_repo(f"{state['owner']}/{state['repo']}")
# # #     file_contents = {}
# # #     for path in file_paths:
# # #         try:
# # #             file = repo.get_contents(path, ref=state["commit_sha"])
# # #             file_contents[path] = file.decoded_content.decode("utf-8")
# # #         except Exception as e:
# # #             print(f"Error reading {path}: {e}")
# # #     return {"file_contents": file_contents}


# # # @tool
# # # def search_code(state: Annotated[Data, InjectedState], query: str):
# # #     """Search for code in the repository."""
# # #     github = get_github_client(state["installation_id"])
# # #     search_query = f"{query} repo:{state['owner']}/{state['repo']}"
# # #     results = github.search_code(search_query)
# # #     files = [result.path for result in results]
# # #     return {"search_results": files}


# # # @tool
# # # def update_file(
# # #     state: Annotated[Data, InjectedState],
# # #     file_path: str,
# # #     operation: Literal["replace", "insert_after", "insert_before", "delete"],
# # #     target: str,
# # #     content: str = "",
# # # ) -> str:
# # #     """
# # #     Stage changes to a repository file.
# # #     The change is stored in state["modified_files"]. No commit is created.
# # #     """
# # #     if file_path in state["modified_files"]:
# # #         file_content = state["modified_files"][file_path]
# # #     elif file_path in state["file_contents"]:
# # #         file_content = state["file_contents"][file_path]
# # #     else:
# # #         return f"Error: '{file_path}' does not exist."

# # #     if operation == "replace":
# # #         if target not in file_content:
# # #             return "Error: target text not found."
# # #         updated = file_content.replace(target, content, 1)
# # #     elif operation == "delete":
# # #         if target not in file_content:
# # #             return "Error: target text not found."
# # #         updated = file_content.replace(target, "", 1)
# # #     elif operation == "insert_after":
# # #         if target not in file_content:
# # #             return "Error: target text not found."
# # #         updated = file_content.replace(target, target + "\n" + content, 1)
# # #     elif operation == "insert_before":
# # #         if target not in file_content:
# # #             return "Error: target text not found."
# # #         updated = file_content.replace(target, content + "\n" + target, 1)
# # #     else:
# # #         return "Error: invalid operation."

# # #     state["modified_files"][file_path] = updated
# # #     return f"Successfully updated '{file_path}'."

# # from typing import Annotated
# # from langgraph.prebuilt import InjectedState
# # from state import Data
# # from langchain_core.tools import tool
# # from typing import Literal
# # from function import get_github_client
# # from dotenv import load_dotenv

# # load_dotenv()

# # @tool
# # def read_file(state: Annotated[Data, InjectedState], file_path: str):
# #     """Read single file from the repository"""
# #     github = get_github_client(state["installation_id"])
# #     repo = github.get_repo(f"{state['owner']}/{state['repo']}")
# #     file = repo.get_contents(file_path, ref=state["commit_sha"])
# #     return {file_path: file.decoded_content.decode("utf-8")}


# # @tool
# # def read_multiple_files(state: Annotated[Data, InjectedState], file_paths: list[str]):
# #     """Read multiple files from repository"""
# #     github = get_github_client(state["installation_id"])
# #     repo = github.get_repo(f"{state['owner']}/{state['repo']}")
# #     file_contents = {}
# #     for path in file_paths:
# #         try:
# #             file = repo.get_contents(path, ref=state["commit_sha"])
# #             file_contents[path] = file.decoded_content.decode("utf-8")
# #         except Exception as e:
# #             print(f"Error reading {path}: {e}")
# #     return {"file_contents": file_contents}


# # @tool
# # def search_code(state: Annotated[Data, InjectedState], query: str):
# #     """Search for code in the repository."""
# #     github = get_github_client(state["installation_id"])
# #     search_query = f"{query} repo:{state['owner']}/{state['repo']}"
# #     results = github.search_code(search_query)
# #     files = [result.path for result in results]
# #     return {"search_results": files}


# # @tool
# # def update_file(
# #     state: Annotated[Data, InjectedState],
# #     file_path: str,
# #     operation: Literal["replace", "insert_after", "insert_before", "delete"],
# #     target: str,
# #     content: str = "",
# # ) -> str:
# #     """
# #     Stage changes to a repository file.
# #     The change is stored in state["modified_files"]. No commit is created.
# #     """
# #     if file_path in state["modified_files"]:
# #         file_content = state["modified_files"][file_path]
# #     elif file_path in state["file_contents"]:
# #         file_content = state["file_contents"][file_path]
# #     else:
# #         return f"Error: '{file_path}' does not exist."

# #     if operation == "replace":
# #         if target not in file_content:
# #             return "Error: target text not found."
# #         updated = file_content.replace(target, content, 1)
# #     elif operation == "delete":
# #         if target not in file_content:
# #             return "Error: target text not found."
# #         updated = file_content.replace(target, "", 1)
# #     elif operation == "insert_after":
# #         if target not in file_content:
# #             return "Error: target text not found."
# #         updated = file_content.replace(target, target + "\n" + content, 1)
# #     elif operation == "insert_before":
# #         if target not in file_content:
# #             return "Error: target text not found."
# #         updated = file_content.replace(target, content + "\n" + target, 1)
# #     else:
# #         return "Error: invalid operation."

# #     state["modified_files"][file_path] = updated
# #     return f"Successfully updated '{file_path}'."

# from typing import Annotated
# from langgraph.prebuilt import InjectedState
# from state import Data
# from langchain_core.tools import tool
# from typing import Literal
# from function import get_github_client
# from dotenv import load_dotenv

# load_dotenv()

# @tool
# def read_file(state: Annotated[Data, InjectedState], file_path: str):
#     """Read single file from the repository"""
#     try:
#         github = get_github_client(state["installation_id"])
#         repo = github.get_repo(f"{state['owner']}/{state['repo']}")
#         file = repo.get_contents(file_path, ref=state["commit_sha"])
#         content = file.decoded_content.decode("utf-8")
#         # merge into existing file_contents rather than overwrite
#         merged = dict(state["file_contents"])
#         merged[file_path] = content
#         return {"file_contents": merged}
#     except Exception as e:
#         return f"Error reading '{file_path}': {e}"


# @tool
# def read_multiple_files(state: Annotated[Data, InjectedState], file_paths: list[str]):
#     """Read multiple files from repository"""
#     github = get_github_client(state["installation_id"])
#     repo = github.get_repo(f"{state['owner']}/{state['repo']}")
#     merged = dict(state["file_contents"])
#     for path in file_paths:
#         try:
#             file = repo.get_contents(path, ref=state["commit_sha"])
#             merged[path] = file.decoded_content.decode("utf-8")
#         except Exception as e:
#             print(f"Error reading {path}: {e}")
#     return {"file_contents": merged}


# @tool
# def search_code(state: Annotated[Data, InjectedState], query: str):
#     """Search for code in the repository."""
#     try:
#         github = get_github_client(state["installation_id"])
#         search_query = f"{query} repo:{state['owner']}/{state['repo']}"
#         results = github.search_code(search_query)
#         files = [result.path for result in results]
#         return f"Found files: {files}"
#     except Exception as e:
#         return f"Error searching code: {e}"


# @tool
# def create_file(state: Annotated[Data, InjectedState], file_path: str, content: str) -> str:
#     """
#     Create a brand-new file in the repository (e.g. requirements.txt, .gitignore).
#     Use this when the file does not already exist. Do NOT use update_file for new files.
#     """
#     if file_path in state["file_contents"] or file_path in state["repository_tree"]:
#         return f"Error: '{file_path}' already exists. Use update_file instead."

#     modified = dict(state["modified_files"])
#     modified[file_path] = content
#     return {"modified_files": modified}


# @tool
# def update_file(
#     state: Annotated[Data, InjectedState],
#     file_path: str,
#     operation: Literal["replace", "insert_after", "insert_before", "delete"],
#     target: str,
#     content: str = "",
# ) -> str:
#     """
#     Stage changes to an EXISTING repository file.
#     You must read the file first with read_file before calling this.
#     Use create_file instead if the file doesn't exist yet.
#     """
#     if file_path in state["modified_files"]:
#         file_content = state["modified_files"][file_path]
#     elif file_path in state["file_contents"]:
#         file_content = state["file_contents"][file_path]
#     else:
#         return f"Error: '{file_path}' has not been read yet. Call read_file first, or use create_file if it's a new file."

#     try:
#         if operation == "replace":
#             if target not in file_content:
#                 return "Error: target text not found."
#             updated = file_content.replace(target, content, 1)
#         elif operation == "delete":
#             if target not in file_content:
#                 return "Error: target text not found."
#             updated = file_content.replace(target, "", 1)
#         elif operation == "insert_after":
#             if target not in file_content:
#                 return "Error: target text not found."
#             updated = file_content.replace(target, target + "\n" + content, 1)
#         elif operation == "insert_before":
#             if target not in file_content:
#                 return "Error: target text not found."
#             updated = file_content.replace(target, content + "\n" + target, 1)
#         else:
#             return "Error: invalid operation."
#     except Exception as e:
#         return f"Error updating '{file_path}': {e}"

#     modified = dict(state["modified_files"])
#     modified[file_path] = updated
#     return {"modified_files": modified}
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
    """Read single file from the repository"""
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
    """Read multiple files from repository"""
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
    """Search for code in the repository."""
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
    Create a brand-new file in the repository.
    Use this when the file does not already exist. Do NOT use update_file for new files.
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
    Stage changes to an EXISTING repository file.
    You must read the file first with read_file before calling this.
    Use create_file instead if the file doesn't exist yet.
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