"""Seed Common Information documents into MongoDB Atlas with embeddings."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from pymongo import MongoClient, UpdateOne

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smart_shopper.config import get_settings
from smart_shopper.tools.common_information import create_embedding


DATA_PATH = ROOT / "data" / "common_information.json"


def _load_dataset() -> list[dict[str, Any]]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        records = json.load(file)

    required_fields = {"title", "category", "question_examples", "content", "source"}
    for index, record in enumerate(records, start=1):
        missing = required_fields - set(record)
        if missing:
            raise ValueError(f"Record #{index} missing fields: {sorted(missing)}")
    return records


def _text_for_embedding(record: dict[str, Any]) -> str:
    examples = " | ".join(record["question_examples"])
    return (
        f"Title: {record['title']}\n"
        f"Category: {record['category']}\n"
        f"Question examples: {examples}\n"
        f"Content: {record['content']}"
    )


def _print_index_definition(embedding_dimensions: int, index_name: str) -> None:
    definition = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": embedding_dimensions,
                "similarity": "cosine",
            },
            {"type": "filter", "path": "category"},
        ]
    }
    print("\nCreate this MongoDB Atlas Vector Search index:")
    print(f"Index name: {index_name}")
    print(json.dumps(definition, indent=2))


def main() -> None:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is required.")
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is required.")

    records = _load_dataset()
    operations = []
    embedding_dimensions = None

    for record in records:
        embedding = create_embedding(_text_for_embedding(record), settings)
        embedding_dimensions = embedding_dimensions or len(embedding)
        document = {
            **record,
            "embedding": embedding,
            "updated_at": datetime.now(timezone.utc),
        }
        operations.append(
            UpdateOne(
                {"title": record["title"], "category": record["category"]},
                {"$set": document},
                upsert=True,
            )
        )

    client = MongoClient(settings.mongodb_uri)
    collection = client[settings.mongodb_db_name][settings.mongodb_common_collection]
    result = collection.bulk_write(operations)

    print(
        "Seed complete: "
        f"matched={result.matched_count}, modified={result.modified_count}, "
        f"upserted={len(result.upserted_ids)}"
    )
    if embedding_dimensions:
        _print_index_definition(embedding_dimensions, settings.mongodb_vector_index)


if __name__ == "__main__":
    main()
