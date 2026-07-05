# # from langchain.agents import create_agent
# # from agent_tools import read_file,read_multiple_files,search_code,update_file
# # from state import Data
# # from langchain_groq import ChatGroq

# # llm=ChatGroq(model="llama-3.3-70b-versatile")
# # tools=[read_file,read_multiple_files,search_code,update_file]

# # agent=create_agent(
# #     model=llm,
# #     tools=tools,
# #     system_prompt = """
# # You are an expert GitHub Actions and CI/CD engineer.

# # Your job is to diagnose GitHub Actions failures.

# # You have access to tools for:
# # - Reading repository files
# # - Reading multiple files
# # - Searching code

# # Rules:
# # 1. Analyze the provided workflow and logs first.
# # 2. Only call tools if additional information is required.
# # 3. Never guess file contents.
# # 4. If the issue is fixable, explain the fix.
# # 5. If the issue cannot be fixed automatically, explain why.
# # 6. Return a clear summary.
# # """
# # )

# # def solveCICD(state:Data):

# #     messages = [
# #             {
# #                 "role": "user",
# #                 "content": f"""
# #         A GitHub Actions workflow failed.

# #         Reason:
# #         {state["reason"]}

# #         Error logs:
# #         {state["logs"]}

# #         Repository tree:
# #         {state["repository_tree"]}

# #         Analyze the failure.
# #         If you need additional information, use the available tools.
# #         If a fix is required, suggest or perform it.
# #         """
# #             }
# #         ]

# #     result=agent.invoke({"messages":messages})
# #     print(result)

# #     return {}
# from langchain.agents import create_agent
# from agent_tools import read_file, read_multiple_files, search_code, update_file
# from state import Data
# from langchain_groq import ChatGroq
# from tenacity import retry, stop_after_attempt, wait_fixed

# llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
# tools = [read_file, read_multiple_files, search_code, update_file]

# agent = create_agent(
#     model=llm,
#     tools=tools,
#     system_prompt="""
# You are an expert GitHub Actions and CI/CD engineer.

# Your job is to diagnose GitHub Actions failures.

# You have access to tools for:
# - Reading repository files
# - Reading multiple files
# - Searching code

# Rules:
# 1. Analyze the provided workflow and logs first.
# 2. Only call tools if additional information is required.
# 3. Never guess file contents.
# 4. If the issue is fixable, explain the fix.
# 5. If the issue cannot be fixed automatically, explain why.
# 6. Return a clear summary.
# 7. When calling a tool, always produce a valid JSON tool call. Do not invent
#    custom syntax. If unsure about parameters, do not call the tool.
# """
# )


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
# def invoke_agent_with_retry(messages):
#     return agent.invoke({"messages": messages})


# def solveCICD(state: Data):

#     # Truncate large fields to reduce malformed tool-call risk
#     logs_snippet = state["logs"][-4000:] if state["logs"] else ""
#     tree_snippet = state["repository_tree"][:50] if state["repository_tree"] else []

#     messages = [
#         {
#             "role": "user",
#             "content": f"""
# A GitHub Actions workflow failed.

# Reason:
# {state["reason"]}

# Error logs (most recent, truncated):
# {logs_snippet}

# Repository tree (truncated to first 50 paths):
# {tree_snippet}

# Analyze the failure.
# If you need additional information, use the available tools.
# If a fix is required, suggest or perform it.
# """
#         }
#     ]

#     try:
#         result = invoke_agent_with_retry(messages)
#         print(result)
#         return {}

#     except Exception as e:
#         print(f"⚠️ Agent failed after retries: {e}")
#         return {
#             "success": False,
#             "root_cause": f"Agent failed during automated fix attempt: {e}",
#         }

from langchain.agents import create_agent
from agent_tools import read_file, read_multiple_files, search_code, update_file,create_file
from state import Data
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, stop_after_attempt, wait_fixed

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [read_file, read_multiple_files, search_code, update_file,create_file]

agent = create_agent(
    model=llm,
    tools=tools,
    state_schema=Data,   # <-- Data used directly, no separate schema
    system_prompt="""
You are an expert GitHub Actions and CI/CD engineer.

Your job is to diagnose GitHub Actions failures.

You have access to tools for:
- Reading repository files
- Reading multiple files
- Searching code
- Creating brand-new files (create_file)
- Updating existing files (update_file)

Rules:
1. Analyze the provided workflow and logs first.
2. Only call tools if additional information is required.
3. Never guess file contents blindly — if creating requirements.txt, package.json,
   or similar dependency files, first read the source code files (.py, .js, etc.)
   in the repository tree to identify actual imports/dependencies used, and include
   them with reasonable version constraints. Do not create an empty dependency file
   unless you have verified via source code that no external dependencies are used.
4. If the issue is fixable, use update_file (for existing files) or create_file
   (for new files) to stage the fix.
5. If the issue cannot be fixed automatically, explain why.
6. Return a clear summary of what was changed and why.
7. When calling a tool, always produce a valid JSON tool call.
"""
)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def invoke_agent_with_retry(payload):
    return agent.invoke(payload)


def solveCICD(state: Data):
    logs_snippet = state["logs"][-4000:] if state["logs"] else ""
    tree_snippet = state["repository_tree"][:50] if state["repository_tree"] else []

#     user_message = {
#         "role": "user",
#         "content": f"""
# A GitHub Actions workflow failed.

# Reason:
# {state["reason"]}

# Error logs (truncated):
# {logs_snippet}

# Repository tree (truncated):
# {tree_snippet}

# Analyze the failure. Use tools if you need to read files.
# If a fix is required, use update_file to stage the change.
# """
#     }

    user_message = {
    "role": "user",
    "content": f"""
A GitHub Actions workflow failed.

Reason:
{state["reason"]}

Error logs (truncated):
{logs_snippet}

Repository tree (truncated):
{tree_snippet}

Analyze the failure. Use tools if you need to read files.
If the fix involves creating a dependency file (requirements.txt, package.json, etc.),
first read the actual source files in the repository to determine real dependencies
before creating the file. Do not create it empty unless you've confirmed no
dependencies are actually used.
If a fix is required, use create_file or update_file to stage the change.
"""
}

    # Data already has every field the tools need — just pass the whole state
    payload = {**state, "messages": [user_message]}

    try:
        result = invoke_agent_with_retry(payload)
        print(result)
        return {
            "modified_files": result.get("modified_files", state["modified_files"])
        }
    except Exception as e:
        print(f"⚠️ Agent failed after retries: {e}")
        return {
            "success": False,
            "root_cause": f"Agent failed during automated fix attempt: {e}",
        }