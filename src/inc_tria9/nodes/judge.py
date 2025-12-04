from typing import Dict, List

from ..state import IncidentState
from ..llm.client import run_sre_judge_llm


def judge(state: IncidentState) -> IncidentState:
    proposals: List[Dict] = state.get("proposals", [])  # type: ignore[assignment]
    incident: Dict = state.get("incident", {})  # type: ignore[assignment]
    print("[judge] evaluating", len(proposals), "proposal(s) via LLM judge")

    if not proposals:
        judgment = {
            "decision": "reject_all",
            "approved": False,
            "reason": "No proposals provided by SRE reviewer.",
            "chosen_index": -1,
            "required_changes": ["Need at least one proposal."],
            "safety_warnings": ["empty_proposals"],
        }
    else:
        judgment = run_sre_judge_llm(proposals=proposals, incident=incident)

    state["judgment"] = judgment
    state["next_node"] = "human_review"
    return state
