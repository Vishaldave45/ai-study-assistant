<div align="center">

# 📚 AI Study Assistant

### AI-powered study & document understanding platform built with **React**, **FastAPI**, **TanStack Table**, **FAISS**, and **Google Gemini**

Upload study materials, organize them into workspaces, inspect documents with smart data tables, generate AI summaries & master revision booklets, track token costs, and interact with your documents using Retrieval-Augmented Generation (RAG).

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6?logo=typescript)
![Vite](https://img.shields.io/badge/Vite-8.1+-646CFF?logo=vite)
![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![TanStack](https://img.shields.io/badge/TanStack-Table%20%26%20Query-FF4154)
![Redux](https://img.shields.io/badge/Redux-Toolkit-764ABC?logo=redux)
![Vitest](https://img.shields.io/badge/Vitest-Unit%20Testing-6E9F18?logo=vitest)
![Playwright](https://img.shields.io/badge/Playwright-E2E%20Testing-2EAD33?logo=playwright)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

# ✨ Overview

**AI Study Assistant** is an enterprise-grade full-stack platform that enables students and researchers to upload study materials and ask grounded questions using Retrieval-Augmented Generation (RAG).

The platform features an **Enterprise React Frontend** with modular domain architecture (`src/modules/`), headless TanStack Data Tables with server-side/client-side mode, React Hook Form + Yup schema validation, Redux Toolkit, base Axios client wrappers, and complete Vitest + Playwright test suites.

---

# 🚀 Features

## 🔐 Authentication & Security
- JWT Authentication (Access & Refresh Tokens with silent auto-refresh interceptors)
- Password Hashing & Protected Route Guards
- React Hook Form + Yup schema validation (`loginSchema`, `registerSchema`)

---

## 📁 Smart Data Table Document Management
- Powered by **@tanstack/react-table** (v8)
- Global text search, per-column text filtering, multi-column sorting, row selection checkboxes, and pagination
- Document preview, metadata inspection, and deletion

---

## 📝 AI Summaries Library & Master Revision Booklet Exporter
- Automatic summary generation for uploaded workspace documents
- **Summaries Library Table** with format filtering (`PDF`, `DOCX`, `TXT`, `MD`), title search, and date sorting
- **Master Revision Booklet Exporter**: Select multiple summaries and export them as a single compiled Markdown booklet (`.md`) or copy to clipboard

---

## ⚡ AI Usage & Token Analytics Table
- Real-time token consumption logger for RAG Chat & AI Summarizer
- KPI metrics summary cards: **Total Queries**, **Total Tokens Used**, **Estimated Cost ($)**, and **Avg Latency (ms)**
- Granular token log table with model tracking (`gemini-2.5-flash`)

---

## 💬 Retrieval-Augmented Generation (RAG) Chat
- Multi-session chat conversations with history persistence
- Paginated message loading powered by TanStack Query (`useChatInfiniteQuery`)
- Citations & document page references for every AI answer

---

# 🏗 System Architecture

```text
               React Frontend (Vite + TypeScript)
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       TanStack Query / Table           Redux Toolkit / Axios
               │                               │
               └───────────────┬───────────────┘
                               │ (REST API / Bearer JWT)
                               ▼
                        FastAPI Server
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
Authentication           Workspace API           Document API
                                                       │
                                                       ▼
                                                PDF/Doc Ingestion
                                                       │
                                                       ▼
                                                Text Processing & Chunking
                                                       │
                                                       ▼
                                                Embedding Service
                                                       │
                                                       ▼
                                                FAISS Vector DB
                                                       │
                                                       ▼
                                              Semantic Retrieval (MMR)
                                                       │
                                                       ▼
                                                Google Gemini LLM
                                                       │
                                                       ▼
                                                Grounded Response
```

---

# 📂 Project Structure

```text
ai-study-assistant/
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── app/                  # FastAPI backend application
│   │   ├── api/v1/           # REST endpoints (auth, workspace, document, chat, summary)
│   │   ├── core/             # Pydantic Settings & security config
│   │   ├── database/         # SQLAlchemy session & models
│   │   ├── rag/              # Vector store, chunking, FAISS retriever, prompts
│   │   └── services/         # Business logic services
│   └── tests/                # Pytest test suite (138 tests)
│
└── frontend/
    ├── e2e/                  # Playwright E2E test specs (auth.spec.ts, documents.spec.ts)
    ├── src/
    │   ├── api/              # Axios & TanStack Query services
    │   ├── base-axios/       # Standardized Axios client & ExtendedResponse wrappers
    │   ├── components/       # Reusable primitives (Button, Modal, ErrorBoundary, DataTable, FormField)
    │   ├── constants/        # HTTP status & navigation route constants
    │   ├── contexts/         # React Context API (Auth, Workspace, Document, Chat)
    │   ├── hooks/            # Custom hooks (useAxios, useChatInfiniteQuery, useAuth, useWorkspace)
    │   ├── modules/          # Domain feature modules (Auth, Documents, Chat, Summary, Analytics)
    │   ├── pages/            # Lazy-loaded route pages (Login, Register, ForgotPassword, ResetPassword)
    │   ├── providers/        # AppProviders wrapping Redux, QueryClient, and Contexts
    │   ├── redux/            # Redux Toolkit store & slices (authSlice, workspaceSlice, uiSlice)
    │   ├── styles/           # Global CSS variables & modern design system
    │   └── test/             # Vitest test setup and unit test specs
    ├── playwright.config.ts  # Playwright E2E configuration
    └── vitest.config.ts      # Vitest unit test configuration
```

---

# 🛠 Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend Core** | React 19, TypeScript, Vite 8 |
| **State Management** | Redux Toolkit (`@reduxjs/toolkit`), React Context API |
| **Data Fetching & Tables** | `@tanstack/react-query` (v5), `@tanstack/react-table` (v8) |
| **Forms & Validation** | `react-hook-form`, `@hookform/resolvers`, `yup` |
| **Networking** | Axios (`base-axios` with JWT interceptors & token refresh) |
| **Frontend Testing** | Vitest, React Testing Library, Playwright E2E |
| **Backend Framework** | Python 3.12, FastAPI, Pydantic v2 |
| **ORM & Database** | SQLAlchemy, Alembic, SQLite / PostgreSQL |
| **Vector Search & LLM** | FAISS, Google Gemini (`gemini-2.5-flash`), Sentence Transformers |
| **Backend Testing** | Pytest (138 tests) |

---

# ⚙️ Installation & Setup

## 1. Backend Setup

```bash
cd backend

# Install uv package manager
pip install uv

# Create virtual environment & sync dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync --all-extras

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload
```
Server runs at: `http://localhost:8000` (API Docs: `http://localhost:8000/docs`)

---

## 2. Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install --legacy-peer-deps

# Start Vite development server
npm run dev
```
Frontend runs at: `http://localhost:5173`

---

# 🧪 Running Tests

### Frontend Unit Tests (Vitest)
```bash
cd frontend
npm test
```

### Frontend E2E Tests (Playwright)
```bash
cd frontend
npm run test:e2e
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

### Backend Test Suite (Pytest)
```bash
cd backend
PYTHONPATH=. .venv/bin/pytest tests/
```

---

# 🛣 Development Roadmap

| Module | Status |
|---|---|
| Authentication & JWT Refresh | ✅ Completed |
| Workspace Management | ✅ Completed |
| PDF Document Upload & Ingestion | ✅ Completed |
| FAISS Vector Search & RAG | ✅ Completed |
| TanStack Smart Data Table | ✅ Completed |
| AI Summaries Library & Booklet Exporter | ✅ Completed |
| AI Usage & Token Analytics Table | ✅ Completed |
| React Hook Form + Yup Validation | ✅ Completed |
| Redux Toolkit State Management | ✅ Completed |
| Vitest & Playwright Testing Suite | ✅ Completed |
| Route Code Splitting (`React.lazy`) | ✅ Completed |
| Concept Explanation & Quizzes | 🚧 In Progress |

---

# 📄 License

This project is licensed under the MIT License.
