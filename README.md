# AI Study Assistant

A full-stack Generative AI web app where students upload PDF study materials and
interact with them through an AI assistant. All answers are grounded in the
uploaded documents via a RAG pipeline, with every response traceable to a
source citation.

## Tech Stack

- **Frontend:** React + TypeScript (Vite), feature-based architecture, Redux Toolkit, react-hook-form, Tailwind CSS, Axios
- **Backend:** FastAPI, layered architecture (API → Service → Orchestration → Provider abstractions)
- **Database:** PostgreSQL (relational) + FAISS (vector search), abstracted for future swap to Chroma/Pinecone
- **LLM:** Gemini (default) / OpenAI, behind a provider-agnostic abstraction layer
- **Orchestration:** LangChain (linear RAG chains) + LangGraph (stateful workflows with conditional loop-backs — quiz regeneration, re-retrieval, ELI10 re-simplification)

## Repository Structure

\`\`\`
ai-study-assistant/
├── frontend/       # React + TS app (feature-based: features/auth, features/chat, ...)
├── backend/        # FastAPI app (layered: api/, services/, rag/, llm/, graphs/, models/)
├── docs/           # Architecture decisions, Obsidian-exportable notes, diagrams
├── scripts/        # Dev/deploy utility scripts (DB seed, migrations helpers, etc.)
├── .env.example    # Deployment-level config template — see docs/architecture.md
└── .gitignore
\`\`\`

## Architecture Principles (non-negotiable)

1. **Provider abstraction everywhere.** LLM, embeddings, and vector store each sit
   behind an interface (\`base.py\`). Swapping a vendor should touch one adapter
   file and one factory entry — never business logic, routes, or graphs.
2. **Strict backend layering.** Routers validate + delegate only. Services own
   business rules. Graphs (LangGraph) orchestrate workflow shape only. No layer
   skips past its neighbor (e.g. graphs never call repositories directly).
3. **Feature-based frontend.** Each feature (\`features/chat/\`, \`features/quiz/\`,
   etc.) is self-contained: components, hooks, api calls, types. \`shared/\` is
   reserved for code used by 2+ features with zero feature-specific logic.
4. **LangGraph only where there's a genuine conditional loop-back**
   (regenerate, re-retrieve, re-simplify). Linear one-shot tasks (e.g.
   summarization) use a plain LangChain chain.
5. **Config vs. Database, decided by change frequency:**
   - Deployment-wide, redeploy-to-change values → \`.env\` / \`config.py\`
     (API keys, default limits, JWT secret).
   - Per-tenant/per-workspace, runtime-changeable values → database
     (per-workspace AI provider, enterprise upload overrides).
6. **No infrastructure before it's proven necessary.** No Redis, Celery, or
   managed vector DB until an actual bottleneck is observed locally.
7. **Every AI answer carries citation metadata** back to its source chunk —
   this shapes the schema and prompts from day one.

Full reasoning and decision logs live in \`docs/\` (see \`docs/architecture.md\`
and per-topic notes, mirrored into Obsidian as the project progresses).

## Getting Started

> Setup instructions will be added at the end of Phase 1 (Auth + Workspace)
> once \`backend/requirements.txt\` and \`frontend/package.json\` exist.

## Build Order

1. Auth + per-user workspace
2. PDF upload → extraction → chunking → embeddings → vector DB
3. Core RAG chat (retrieval + generation + citations)
4. Semantic search
5. Document summarization
6. AI quiz generator
7. Flashcard generation
8. Explain Like I'm 10
9. Persistent chat history
10. UI/UX polish
11. Deployment
