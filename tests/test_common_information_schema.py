import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "common_information.json"


def test_common_information_dataset_schema():
    records = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    assert len(records) >= 10
    required_fields = {"title", "category", "question_examples", "content", "source"}
    categories = {record["category"] for record in records}

    for record in records:
        assert required_fields <= set(record)
        assert isinstance(record["question_examples"], list)
        assert record["question_examples"]
        assert len(record["content"]) > 80

    assert {
        "shipping",
        "purchase",
        "payment",
        "refund",
        "return",
        "cancellation",
        "warranty",
        "tracking",
        "account",
        "promo",
    } <= categories
