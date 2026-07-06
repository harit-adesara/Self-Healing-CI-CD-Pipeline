from langgraph.graph import StateGraph,START,END
from state import Data
from agent import solveCICD
from function import check_branch,commitMsg,successMail,commit,download_workflow_logs,fetch_tree,classify_error,divide_flow_based_on_fixability,sendEmail,create_branch,suggestFix

graph=StateGraph(Data)

graph.add_node("download_logs",download_workflow_logs)
graph.add_node("fetch_tree",fetch_tree)
graph.add_node("classify_error",classify_error)
graph.add_node("create_branch",create_branch)
graph.add_node("suggest_fix",suggestFix)
graph.add_node("sendEmail",sendEmail)
graph.add_node("solve_CICD",solveCICD)
graph.add_node("commit",commit)
graph.add_node("success_mail",successMail)
graph.add_node("commitMsg",commitMsg)

graph.add_conditional_edges(START,check_branch,{"suggest":"suggest_fix","logs":"download_logs"})
graph.add_edge("download_logs","fetch_tree")
graph.add_edge("fetch_tree","classify_error")
graph.add_conditional_edges("classify_error",divide_flow_based_on_fixability,{"solve":"create_branch","suggest":"suggest_fix"})
graph.add_edge("create_branch","solve_CICD")
graph.add_edge("solve_CICD","commitMsg")
graph.add_edge("commitMsg","commit")

workflow=graph.compile()
