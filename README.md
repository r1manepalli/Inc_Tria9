# Inc_Tria9

Incident triage LangGraph skeleton with:

- Orchestrator node
- SRE reviewer node (FAISS runbook vector DB + **OpenAI LLM**)
- Judge node (**expert SRE with a critical eye**, powered by OpenAI LLM)
- **Human review node** (mandatory checkpoint after judge)
- Action node wired to an MCP action stub

Observability is provided via **LangSmith**. The project is wired to use
LangChain's integration with LangSmith, so LLM calls will be traced as long as
you set the correct environment variables.

## Tech Summary

- **Orchestrator**: routes between reviewer, judge, human, and action nodes
- **SRE Reviewer**: expert SRE persona that reads FAISS-backed runbooks and
  synthesizes diagnostic / remediation / rollback plans via OpenAI
- **Judge**: expert SRE with a critical eye that evaluates proposals and
  prepares a plan for human approval
- **Human Review**: simulated human SRE approval point (replace with your UI)
- **Action (MCP)**: stub where you connect your MCP server tools
- **Vector DB**: FAISS + sentence-transformers
- **LLM**: OpenAI (via langchain-openai ChatOpenAI wrapper)
- **Observability**: LangSmith traces for LLM calls

## Environment configuration inside the project

An example environment file is included at the project root:

- `.env.example`

Copy it to `.env` and adjust values as needed:

```bash
cp .env.example .env
```

Then fill in:

- `OPENAI_API_KEY`
- `OPENAI_MODEL_REVIEWER`, `OPENAI_MODEL_JUDGE` (optional)
- `LANGCHAIN_TRACING_V2`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`
- `RUNBOOK_SOURCE_DIR` (optional for the index builder)

You can load this `.env` file using tools like `direnv` or `python-dotenv` in your own tooling,
or simply export the variables manually in your shell.

## FAISS index builder script

A minimal FAISS index builder script is provided:

- `src/inc_tria9/build_runbook_index.py`

By default it reads runbooks from `./runbooks` (or `RUNBOOK_SOURCE_DIR`) and writes:

- `data/runbooks/runbooks.index.faiss`
- `data/runbooks/runbooks.meta.json`

### Running the index builder

From the project root:

```bash
# Ensure dependencies are installed
poetry install

# (Optional) point to your runbooks directory
export RUNBOOK_SOURCE_DIR="./runbooks"

# Run the builder
poetry run python -m inc_tria9.build_runbook_index
```

After this, the `sre_reviewer` node will retrieve real runbook chunks from FAISS instead
of the synthetic fallback.

## Quick Start for the graph

```bash
# Install dependencies
poetry install

# Run the demo (will gracefully fall back if FAISS index is missing)
poetry run python -m inc_tria9.main
```
