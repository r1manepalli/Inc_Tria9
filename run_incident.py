"""
Run an incident through the LangGraph pipeline.

Usage:
    poetry run python run_incident.py incidents/incident_checkout.json
"""

import json
import sys
from pathlib import Path

from src.inc_tria9.graph import build_graph
from langgraph.checkpoint.memory import MemorySaver


def main():
    if len(sys.argv) != 2:
        print("Usage: python run_incident.py <incident_json_path>")
        sys.exit(1)

    incident_path = Path(sys.argv[1])
    data = json.loads(incident_path.read_text())

    workflow = build_graph()
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    print("\n=== Running Incident ===\n")
    print(json.dumps(data["incident"], indent=2))

    # Use incident id as thread_id for the checkpointer / LangSmith
    thread_id = data["incident"].get("id", "default-thread")

    for step in app.stream(data, {"configurable": {"thread_id": thread_id}}):
        print("\n--- Step Output ---\n")
        print(step)

    print("\n=== DONE ===\n")


if __name__ == "__main__":
    main()
