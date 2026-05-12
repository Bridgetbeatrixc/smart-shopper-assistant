"""Common Information RAG tool backed by MongoDB Atlas Vector Search."""

from __future__ import annotations

from typing import Any

from smart_shopper.config import Settings, get_settings


LOW_CONFIDENCE_THRESHOLD = 0.65


def _missing_config(settings: Settings) -> list[str]:
    missing = []
    if not settings.google_api_key:
        missing.append("GOOGLE_API_KEY")
    if not settings.mongodb_uri:
        missing.append("MONGODB_URI")
    return missing


def _embedding_client(settings: Settings) -> genai.Client:
    from google import genai

    return genai.Client(api_key=settings.google_api_key)


def create_embedding(text: str, settings: Settings | None = None) -> list[float]:
    """Create an embedding vector for text using the configured Gemini model."""

    active_settings = settings or get_settings()
    missing = _missing_config(active_settings)
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    client = _embedding_client(active_settings)
    response = client.models.embed_content(
        model=active_settings.embedding_model,
        contents=text,
    )
    return list(response.embeddings[0].values)


def _get_collection(settings: Settings):
    from pymongo import MongoClient

    client = MongoClient(settings.mongodb_uri)
    database = client[settings.mongodb_db_name]
    return database[settings.mongodb_common_collection]


def _retrieve_documents(query: str, settings: Settings, limit: int = 4) -> list[dict[str, Any]]:
    query_embedding = create_embedding(query, settings)
    collection = _get_collection(settings)
    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.mongodb_vector_index,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "category": 1,
                "content": 1,
                "source": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    return list(collection.aggregate(pipeline))


def _generate_answer(query: str, documents: list[dict[str, Any]], settings: Settings) -> str:
    context = "\n\n".join(
        f"Judul: {doc['title']}\nKategori: {doc['category']}\nIsi: {doc['content']}"
        for doc in documents
    )
    prompt = f"""
Anda adalah assistant e-commerce. Jawab pertanyaan user hanya berdasarkan
konteks berikut. Jika konteks tidak cukup, katakan bahwa informasi belum
tersedia di knowledge base.

Pertanyaan user:
{query}

Konteks:
{context}

Jawaban harus dalam Bahasa Indonesia, ringkas, dan berbentuk poin praktis.
"""
    client = _embedding_client(settings)
    response = client.models.generate_content(
        model=settings.generation_model,
        contents=prompt,
    )
    return response.text or "Informasi belum tersedia di knowledge base saat ini."


def retrieve_common_information(query: str) -> dict[str, Any]:
    """Retrieve and answer common e-commerce information questions using RAG.

    Use this tool for shipping, buying flow, payment, refund, return,
    cancellation, warranty, tracking, account, promo, voucher, or marketplace
    policy questions.

    Args:
        query: User question about common e-commerce information.
    """

    settings = get_settings()
    missing = _missing_config(settings)
    if missing:
        return {
            "status": "configuration_required",
            "answer": (
                "Common Information RAG belum bisa dijalankan karena environment "
                f"variable berikut belum diisi: {', '.join(missing)}."
            ),
            "category": None,
            "sources": [],
        }

    try:
        documents = _retrieve_documents(query, settings)
    except Exception as exc:
        return {
            "status": "retrieval_error",
            "answer": f"Gagal mengambil data Common Information: {exc}",
            "category": None,
            "sources": [],
        }

    if not documents or documents[0].get("score", 0) < LOW_CONFIDENCE_THRESHOLD:
        return {
            "status": "not_found",
            "answer": (
                "Informasi tersebut belum tersedia di knowledge base Common "
                "Information saat ini."
            ),
            "category": None,
            "sources": [],
        }

    try:
        answer = _generate_answer(query, documents, settings)
    except Exception as exc:
        return {
            "status": "generation_error",
            "answer": f"Dokumen ditemukan, tetapi generation gagal: {exc}",
            "category": documents[0].get("category"),
            "sources": [
                {"title": doc["title"], "source": doc.get("source"), "score": doc.get("score")}
                for doc in documents
            ],
        }

    return {
        "status": "success",
        "answer": answer,
        "category": documents[0].get("category"),
        "sources": [
            {"title": doc["title"], "source": doc.get("source"), "score": doc.get("score")}
            for doc in documents
        ],
    }
