from ..state import IncidentState


def human_review(state: IncidentState) -> IncidentState:
    """Human-in-the-loop checkpoint (simulated)."""
    judgment = state.get("judgment", {})
    print("[human_review] simulated human is reviewing the judgment...")

    human_decision = {
        "approved": True,
        "approver": "simulated.sre@example.com",
        "comment": "Looks good. Please proceed but monitor error rate for 10 minutes post-change.",
        "based_on_judgment": judgment,
    }

    state["human_decision"] = human_decision
    state["next_node"] = "action_mcp"
    return state
