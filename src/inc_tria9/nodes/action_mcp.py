from typing import Any, Dict, List

from ..state import IncidentState


def _execute_actions_via_mcp(human_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Stub: place to call MCP tools."""
    return [
        {
            "tool": "mcp.restart_service",
            "status": "success",
            "details": "Simulated restart of checkout service deployment.",
            "human_comment": human_decision.get("comment"),
        }
    ]


def action_mcp(state: IncidentState) -> IncidentState:
    human_decision: Dict[str, Any] = state.get("human_decision", {})  # type: ignore[assignment]
    print("[action_mcp] executing approved actions via MCP (simulated)...")

    actions = _execute_actions_via_mcp(human_decision)
    state["actions"] = actions
    state["done"] = True
    state["next_node"] = None
    return state
