"""Google ADK root agent for SmartShopper Assistant."""

from google.adk.agents import Agent

from smart_shopper.config import get_settings
from smart_shopper.tools.common_information import retrieve_common_information
from smart_shopper.tools.product_recommendation import recommend_products


settings = get_settings()

ROOT_AGENT_INSTRUCTION = """
Anda adalah Personalized SmartShopper Assistant untuk konteks e-commerce.
Jawab dalam Bahasa Indonesia secara ringkas, terstruktur, dan kontekstual,
kecuali user meminta bahasa lain.

Gunakan tool recommend_products untuk pertanyaan tentang rekomendasi produk,
pencarian produk, perbandingan produk, kategori, spesifikasi, budget, atau
"produk apa yang cocok".

Gunakan tool retrieve_common_information untuk pertanyaan umum tentang proses
jual-beli, termasuk pengiriman, cara pembelian, pembayaran, refund, retur,
pembatalan, garansi, pelacakan pesanan, akun, promo, voucher, dan kebijakan
marketplace.

Untuk pertanyaan campuran, panggil kedua tool yang relevan lalu gabungkan
jawaban dengan jelas. Jangan mengarang kebijakan atau detail produk yang tidak
didukung hasil tool. Jika informasi tidak tersedia, katakan dengan jujur dan
sarankan langkah aman berikutnya.
"""


root_agent = Agent(
    model=settings.generation_model,
    name="personalized_smart_shopper_assistant",
    description=(
        "AI assistant for product recommendations and common e-commerce "
        "information using Google ADK tools."
    ),
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[recommend_products, retrieve_common_information],
)
