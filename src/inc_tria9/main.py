"""Small demo entrypoint for the Inc_Tria9 graph."""

from langgraph.checkpoint.memory import MemorySaver

from .graph import build_graph
from .state import IncidentState


def run_demo() -> None:
    workflow = build_graph()
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    initial_state: IncidentState = {
        "incident": {
            "id": "INC-12345",
            "summary": "High error rate on checkout service",
            "severity": "P1",
            "source": "dynatrace",
            "service": "checkout-api",
        },
        "next_node": "sre_reviewer",
    }

    for event in app.stream(initial_state, {"configurable": {"thread_id": "demo"}}):
        print("--- EVENT ---")
        print(event)


if __name__ == "__main__":
    run_demo()
