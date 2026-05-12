from smart_shopper.tools.common_information import retrieve_common_information
from smart_shopper.tools.product_recommendation import recommend_products


def test_product_recommendation_detects_budget_and_category():
    result = recommend_products("Rekomendasikan headphone untuk meeting di bawah 500 ribu")

    assert result["status"] == "success"
    assert result["budget_detected"] == 500_000
    assert result["recommendations"][0]["category"] == "headphone"
    assert result["recommendations"][0]["price"] <= 500_000


def test_product_recommendation_powerbank():
    result = recommend_products("Saya butuh powerbank untuk travel")

    assert result["status"] == "success"
    assert result["recommendations"][0]["category"] == "powerbank"


def test_common_information_reports_missing_configuration(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("MONGODB_URI", raising=False)

    result = retrieve_common_information("Bagaimana cara refund kalau barang rusak?")

    assert result["status"] == "configuration_required"
    assert "GOOGLE_API_KEY" in result["answer"]
    assert "MONGODB_URI" in result["answer"]
