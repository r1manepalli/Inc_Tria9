from typing import Any, Dict, List

from ..state import IncidentState
from ..vector_db.retriever import retrieve_runbooks
from ..llm.client import run_sre_reviewer_llm


def sre_reviewer(state: IncidentState) -> IncidentState:
    incident = state.get("incident", {})
    print("[sre_reviewer] drafting proposal for incident", incident.get("id"))

    query = incident.get("summary") or "production incident"
    metadata_filter = {}
    if "service" in incident:
        metadata_filter["service"] = incident["service"]

    runbooks = retrieve_runbooks(query=query, top_k=5, metadata_filter=metadata_filter)
    proposal = run_sre_reviewer_llm(incident=incident, runbooks=runbooks)

    existing = state.get("proposals") or []
    existing.append(proposal)
    state["proposals"] = existing

    state["next_node"] = "judge"
    return state
