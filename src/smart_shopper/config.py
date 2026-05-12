"""Configuration helpers for environment-driven services."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    google_api_key: str | None
    mongodb_uri: str | None
    mongodb_db_name: str
    mongodb_common_collection: str
    mongodb_vector_index: str
    embedding_model: str
    generation_model: str


def get_settings() -> Settings:
    """Read application settings from environment variables."""

    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        mongodb_uri=os.getenv("MONGODB_URI"),
        mongodb_db_name=os.getenv("MONGODB_DB_NAME", "smart_shopper"),
        mongodb_common_collection=os.getenv(
            "MONGODB_COMMON_COLLECTION", "common_information"
        ),
        mongodb_vector_index=os.getenv(
            "MONGODB_VECTOR_INDEX", "common_info_vector_index"
        ),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-004"),
        generation_model=os.getenv("GENERATION_MODEL", "gemini-2.0-flash"),
    )
