from ..state import IncidentState


def orchestrator(state: IncidentState) -> IncidentState:
    """Central routing node."""
    print("[orchestrator] current next_node=", state.get("next_node"))

    if state.get("done") is True:
        state["next_node"] = None
        return state

    if "next_node" not in state or state["next_node"] is None:
        state["next_node"] = "sre_reviewer"

    return state
