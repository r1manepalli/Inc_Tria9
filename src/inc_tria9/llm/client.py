from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def _make_reviewer_llm() -> ChatOpenAI:
    """
    LLM used by the SRE reviewer node.
    """
    model = os.getenv("OPENAI_MODEL_REVIEWER", "gpt-4.1-mini")
    return ChatOpenAI(model=model, temperature=0.2)


def _make_judge_llm() -> ChatOpenAI:
    """
    LLM used by the SRE judge node.
    """
    model = os.getenv("OPENAI_MODEL_JUDGE", "gpt-4.1")
    return ChatOpenAI(model=model, temperature=0.1)


def run_sre_reviewer_llm(incident: Dict[str, Any], runbooks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Call OpenAI as an expert SRE reviewer.

    Returns a structured dict with diagnostic_steps, remediation_plan,
    rollback_plan, etc.
    """
    llm = _make_reviewer_llm()

    system = SystemMessage(
        content=(
            "You are an expert Site Reliability Engineer (SRE) responsible for "
            "triaging production incidents. You are calm, methodical, and "
            "safety-focused.\n\n"
            "You will be given:\n"
            "1) A JSON description of a production incident\n"
            "2) A list of runbook chunks retrieved from a vector database\n\n"
            "Your job is to synthesize a clear, actionable plan that a human SRE "
            "could follow. You MUST respond in strict JSON with the following keys:\n"
            "- incident_summary: short string\n"
            "- service: short string\n"
            "- used_runbook_ids: list of strings\n"
            "- diagnostic_steps: list of short, ordered strings\n"
            "- remediation_plan: list of short, ordered strings\n"
            "- rollback_plan: list of short, ordered strings\n"
            "- referenced_runbook_snippets: list of short strings\n"
            "- risk_flags: list of short strings\n"
            "- confidence: number between 0 and 1\n"
        )
    )

    human = HumanMessage(
        content=(
            "INCIDENT JSON:\n"
            f"{incident}\n\n"
            "RUNBOOK CHUNKS (each has id, text, metadata, score):\n"
            f"{runbooks}\n\n"
            "Now produce the JSON response as specified."
        )
    )

    resp = llm.invoke([system, human])

    try:
        data = json.loads(resp.content)  # type: ignore[arg-type]
    except Exception:
        # Fallback: return a minimal structure if parsing fails
        data = {
            "incident_summary": incident.get("summary", "Unknown incident"),
            "service": incident.get("service", "unknown-service"),
            "used_runbook_ids": [rb.get("id", "unknown") for rb in runbooks],
            "diagnostic_steps": [
                "Inspect recent error spikes and latency for the affected service.",
                "Check logs and recent deployments around the time of impact.",
            ],
            "remediation_plan": [
                "If a recent deployment correlates with the incident, "
                "roll back to the previous known-good version."
            ],
            "rollback_plan": [
                "Redeploy the previous known-good artifact via the standard pipeline."
            ],
            "referenced_runbook_snippets": [rb.get("text", "") for rb in runbooks[:3]],
            "risk_flags": ["LLM_parse_error_fallback"],
            "confidence": 0.5,
        }
    return data


def run_sre_judge_llm(proposals: List[Dict[str, Any]], incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call OpenAI as an expert SRE judge with a critical eye.

    The judge reviews the list of proposals and returns a decision structure.
    """
    llm = _make_judge_llm()

    system = SystemMessage(
        content=(
            "You are an expert Site Reliability Engineer (SRE) acting as a "
            "critical reviewer of remediation plans for production incidents.\n\n"
            "You will be given:\n"
            "1) A JSON description of the incident\n"
            "2) A list of one or more SRE proposals (each with diagnostic_steps, "
            "remediation_plan, etc.)\n\n"
            "Your job is to:\n"
            "- Identify the best proposal (or reject them all)\n"
            "- Highlight any obvious safety issues, blast radius risks, or missing steps\n"
            "- Decide whether the plan is ready to send to a human SRE for approval\n\n"
            "You MUST respond in strict JSON with the following keys:\n"
            "- decision: one of 'proceed_to_human_review', 'needs_more_work', 'reject_all'\n"
            "- approved: boolean indicating whether this is good enough to show a human\n"
            "- reason: short string explanation\n"
            "- chosen_index: integer index of the chosen proposal (or -1 if rejected)\n"
            "- required_changes: list of short strings describing required improvements\n"
            "- safety_warnings: list of short strings\n"
        )
    )

    human = HumanMessage(
        content=(
            "INCIDENT JSON:\n"
            f"{incident}\n\n"
            "SRE PROPOSALS:\n"
            f"{proposals}\n\n"
            "Now produce the JSON response as specified."
        )
    )

    resp = llm.invoke([system, human])

    try:
        data = json.loads(resp.content)  # type: ignore[arg-type]
    except Exception:
        # Fallback behaviour if parsing fails
        if not proposals:
            return {
                "decision": "reject_all",
                "approved": False,
                "reason": "No proposals provided.",
                "chosen_index": -1,
                "required_changes": ["Need at least one proposal."],
                "safety_warnings": ["LLM_parse_error_fallback"],
            }
        best_idx = max(
            range(len(proposals)), key=lambda i: proposals[i].get("confidence", 0.0)
        )
        return {
            "decision": "proceed_to_human_review",
            "approved": False,
            "reason": "Falling back to local heuristic; chose best-confidence proposal.",
            "chosen_index": best_idx,
            "required_changes": [
                "Have a human SRE double-check remediation steps."
            ],
            "safety_warnings": ["LLM_parse_error_fallback"],
        }

    return data
