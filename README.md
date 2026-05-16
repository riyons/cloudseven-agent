# CloudSeven Agent

A production-grade agentic customer-service chatbot for the fictional **CloudSeven Airlines**. Built as a learning project to explore semantic routing, tool calling, RAG, and guardrails using LangGraph.

> **Status:** Phase 1 — simple chat loop with local LLM (Ollama).
> Will evolve into a full LangGraph agent with tool calling, RAG, and FastAPI deployment.

---

## Quick start

```bash
# 1. Clone & set up env
git clone <your-repo-url> cloudseven-agent
cd cloudseven-agent
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install
pip install -e ".[dev]"

# 3. Configure
cp .env.example .env
# (defaults are fine for Phase 1)

# 4. Make sure Ollama is running and you have the model
ollama pull qwen2.5:14b            # or llama3.2:3b for lower-RAM machines

# 5. Chat!
make chat
# or: python -m scripts.chat
```

---

## Architecture

Designed so that **every external dependency is swappable** without touching business logic.

```
┌─────────────────────────────────────────────────┐
│  scripts/chat.py   (entry point: CLI)           │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  agent/                                         │
│   Conversation, prompts, (later) LangGraph      │
└──────┬──────────────────────────┬───────────────┘
       │                          │
┌──────▼──────────┐    ┌──────────▼─────────────┐
│  llm/           │    │  repositories/         │
│   LLMClient     │    │   FlightRepository     │
│   (Protocol)    │    │   BookingRepository    │
│                 │    │   LoyaltyRepository    │
│  ↳ Ollama       │    │   (Protocols)          │
│  ↳ Anthropic    │    │                        │
│                 │    │  ↳ JSON impl           │
│                 │    │  ↳ API impl (later)    │
└─────────────────┘    └────────────────────────┘
                                  │
                       ┌──────────▼─────────────┐
                       │  domain/               │
                       │   Flight, Booking, …   │
                       │   (Pydantic models)    │
                       └────────────────────────┘
```

**Key principle:** The `agent/` layer never imports concrete LLM or repository classes — only their protocols. Swapping `ollama` → `anthropic` or `json` → `api` is a one-line config change.

### Layers, top to bottom

| Layer | Purpose | Knows about |
|---|---|---|
| `scripts/` | Entry points (CLI now, API later) | everything below |
| `agent/` | Conversation orchestration & prompts | `llm`, `repositories`, `domain` |
| `tools/` | Tool functions the LLM can call | `repositories`, `domain` |
| `retrieval/` | RAG (Phase 4+) | `domain` |
| `guardrails/` | Safety checks (Phase 5+) | `domain` |
| `llm/` | LLM provider abstraction | `domain` |
| `repositories/` | Data access (JSON → API later) | `domain` |
| `domain/` | Pure business models | nothing |
| `config.py` | Settings loaded from `.env` | nothing |

---

## Roadmap

Revised plan that incorporates core AI Engineering concepts (semantic routing, tool calling, RAG, evals, MCP, guardrails) as natural project phases. Each phase builds on the previous and produces a working, demonstrable system.

### Core phases (MVP)

- [x] **Phase 1 — Foundation**
  Simple chat loop with Ollama, structured logging, configuration layer, repository pattern, LLM abstraction.
  *Concepts: project architecture, dependency injection, layered design.*

- [ ] **Phase 2 — Tool calling (ReAct loop)**
  Tools: `get_flight_status`, `lookup_booking`, `get_loyalty_balance`, `search_flights`. Manual agent loop first, before any framework.
  *Concepts: ReAct pattern, tool schemas, agent reasoning loop, transient vs. permanent failures.*

- [ ] **Phase 3 — LangGraph + semantic routing + tracing**
  Rewrite the manual agent loop as a LangGraph with conditional edges. Semantic router classifies queries (`flight_info`, `booking`, `baggage`, `loyalty`, `escalation`). Add LangSmith for tracing.
  *Concepts: state machines, conditional routing, embeddings for classification, observability.*

- [ ] **Phase 4 — RAG over policies**
  Embed policy markdown into Chroma using sentence-transformers. Hybrid search (vector + BM25). Citations in answers.
  *Concepts: chunking, embeddings, vector DBs, hybrid search, RAGAS evaluation.*

- [ ] **Phase 5 — Guardrails**
  Input checks: PII detection (Presidio), prompt-injection defence, off-topic filter. Output checks: hallucination detection (citation grounding), PII redaction, scope enforcement.
  *Concepts: input/output guardrails, PII handling, prompt injection, sandboxed execution.*

- [ ] **Phase 6 — FastAPI + evals + deployment**
  Wrap in a FastAPI service with session management. Golden-set eval suite. Docker + docker-compose. Optional minimal frontend.
  *Concepts: API design, offline/online evals, LLM-as-judge, human-in-the-loop review, deployment.*

### Extension phases (post-MVP, optional but high-value)

- [ ] **Phase 7 — Expose tools as MCP server**
  Refactor CloudSeven's tools as a [Model Context Protocol](https://modelcontextprotocol.io) server. Same tools, but now any MCP-compatible client (Claude Desktop, Cursor, custom agents) can use them.
  *Concepts: MCP fundamentals, AI interoperability standards.*

- [ ] **Phase 8 — Text-to-SQL extension**
  Add a SQL-backed `PostgresFlightRepository` and a `query_flights_sql` tool that lets the agent generate SQL for complex queries ("delayed flights from Kochi this week"). Includes self-correction loop.
  *Concepts: text-to-SQL agents, self-correcting agents, complex tool design.*

### Stretch phases (portfolio standouts)

- [ ] **Phase 9 — Cost optimization at scale**
  Semantic caching of common questions. Smart routing: cheap model for simple intents, capable model for complex reasoning.
  *Concepts: semantic caching, model routing, cost engineering.*

- [ ] **Phase 10 — Pick one: voice OR multimodal**
  *Voice:* phone-style interface with Deepgram STT + TTS + LiveKit, low-latency turn-taking.
  *Multimodal:* "upload a photo of damaged baggage" → vision model extracts info → agent files a claim.
  *Concepts: real-time voice stacks, multimodal RAG, vision models.*

### What this roadmap deliberately skips

- Fine-tuning, LoRA, synthetic data pipelines — RAG + good prompting handle 95% of use cases at the application layer.
- Reinforcement learning, GRPO — research-level, rarely applied in production agent systems.
- Building custom LLMs or vector DBs — these are commodity infrastructure; use what exists.

---

## Project layout

```
cloudseven-agent/
├── data/                # fake JSON data + policy markdown (swap for real APIs later)
├── docs/                # learning guide PDF, architecture diagrams
├── src/cloudseven/
│   ├── domain/          # Pydantic models — the stable core
│   ├── repositories/    # data access (JSON now, API later)
│   ├── llm/             # LLM provider abstraction
│   ├── agent/           # conversation logic & prompts (LangGraph in Phase 3)
│   ├── tools/           # tool functions (Phase 2)
│   ├── retrieval/       # RAG (Phase 4)
│   ├── guardrails/      # safety (Phase 5)
│   └── api/             # FastAPI (Phase 6)
├── scripts/             # CLI entry points
└── tests/               # pytest
```

---

## Development

```bash
make chat       # run the CLI chatbot
make test       # run pytest
make lint       # ruff + mypy
make format     # auto-format
make clean      # delete caches
```

---

## Why this exists

Built in public as a portfolio project. See `docs/CloudSeven_Learning_Guide.pdf` for the full learning journey, concepts explained, and FAQs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE)

---

## Disclaimer

*CloudSeven Airlines is a fictional airline created for educational purposes.
This project is not affiliated with any real airline, company, or brand named
"Cloud Seven," "Cloud 7," or any variant thereof.*
