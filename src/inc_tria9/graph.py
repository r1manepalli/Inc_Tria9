from typing import Literal

from langgraph.graph import StateGraph, END

from .state import IncidentState
from .nodes.orchestrator import orchestrator
from .nodes.sre_reviewer import sre_reviewer
from .nodes.judge import judge
from .nodes.human_review import human_review
from .nodes.action_mcp import action_mcp


def _route_from_orchestrator(state: IncidentState) -> Literal["sre_reviewer", "judge", "human_review", "action_mcp", "end"]:
    """Simple router that looks at state['next_node']."""
    target = state.get("next_node", "sre_reviewer")
    if target not in {"sre_reviewer", "judge", "human_review", "action_mcp"}:
        return "end"
    return target  # type: ignore[return-value]


def build_graph() -> StateGraph:
    workflow = StateGraph(IncidentState)

    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("sre_reviewer", sre_reviewer)
    workflow.add_node("judge", judge)
    workflow.add_node("human_review", human_review)
    workflow.add_node("action_mcp", action_mcp)

    workflow.set_entry_point("orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        _route_from_orchestrator,
        {
            "sre_reviewer": "sre_reviewer",
            "judge": "judge",
            "human_review": "human_review",
            "action_mcp": "action_mcp",
            "end": END,
        },
    )

    workflow.add_edge("sre_reviewer", "orchestrator")
    workflow.add_edge("judge", "orchestrator")
    workflow.add_edge("human_review", "orchestrator")
    workflow.add_edge("action_mcp", END)

    return workflow
