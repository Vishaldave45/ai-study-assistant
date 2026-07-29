#!/usr/bin/env python3
"""
Real Retrieval Evaluation Script for FAISS Vector Store and SentenceTransformers Embeddings.
Computes Hit Rate@k and Mean Reciprocal Rank (MRR@k) on golden dataset queries.
"""
import sys
import json
import argparse
from uuid import UUID
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.retrieval.service import RetrievalService


def evaluate_retrieval(workspace_id: str, dataset_path: str, top_k: int = 5):
    db = SessionLocal()
    try:
        ws_uuid = UUID(workspace_id)
        with open(dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        retrieval_service = RetrievalService(db)
        hits = 0
        reciprocal_ranks = []

        print(f"\n==================================================")
        print(f"📊 RAG Retrieval Benchmark (Workspace: {workspace_id})")
        print(f"==================================================\n")

        for idx, item in enumerate(dataset, 1):
            query = item["query"]
            target_doc = item.get("target_document")
            keywords = item.get("target_keywords", [])

            try:
                res = retrieval_service.retrieve(workspace_id=ws_uuid, query=query, top_k=top_k)
                retrieved_chunks = res.chunks
            except Exception as e:
                print(f"[{idx}] ❌ Query failed: '{query}' -> Error: {e}")
                reciprocal_ranks.append(0.0)
                continue

            first_rank = None
            for rank, chunk in enumerate(retrieved_chunks, 1):
                doc_name = chunk.metadata.get("original_filename", "")
                text_content = chunk.text.lower()

                # Match against target document filename or keyword overlap
                doc_match = target_doc and target_doc.lower() in doc_name.lower()
                kw_match = any(kw.lower() in text_content for kw in keywords)

                if doc_match or kw_match:
                    first_rank = rank
                    break

            if first_rank is not None:
                hits += 1
                rr = 1.0 / first_rank
                reciprocal_ranks.append(rr)
                print(f"[{idx}] ✅ '{query}' -> Hit at Rank {first_rank} (RR: {rr:.4f})")
            else:
                reciprocal_ranks.append(0.0)
                print(f"[{idx}] ⚠️ '{query}' -> No relevant match in top {top_k}")

        total_queries = len(dataset)
        hit_rate = (hits / total_queries) * 100.0 if total_queries > 0 else 0.0
        mrr = (sum(reciprocal_ranks) / total_queries) if total_queries > 0 else 0.0

        print(f"\n==================================================")
        print(f"🎯 Final Retrieval Benchmark Results:")
        print(f"   • Evaluated Queries: {total_queries}")
        print(f"   • Hit Rate @ {top_k}: {hit_rate:.2f}%")
        print(f"   • MRR @ {top_k}:      {mrr:.4f}")
        print(f"==================================================\n")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG Retrieval Performance")
    parser.add_argument("--workspace-id", required=True, help="Target workspace UUID")
    parser.add_argument("--dataset", default="scripts/golden_eval_dataset.json", help="Path to golden dataset JSON")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K chunks to evaluate")

    args = parser.parse_args()
    evaluate_retrieval(args.workspace_id, args.dataset, args.top_k)
