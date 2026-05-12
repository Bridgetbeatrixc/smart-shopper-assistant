# Personalized SmartShopper Assistant

Personalized SmartShopper Assistant adalah mini project AI Agent untuk konteks e-commerce. Agent dibuat dengan Google ADK, memiliki tool rekomendasi produk, dan tool Common Information berbasis RAG menggunakan MongoDB Atlas Vector Search.

## Analisis Kebutuhan

Pertanyaan **product** adalah pertanyaan yang membutuhkan rekomendasi, pencarian, perbandingan, kategori, spesifikasi, budget, atau kecocokan produk. Contoh: `Rekomendasikan headphone untuk meeting di bawah 500 ribu`.

Pertanyaan **common information** adalah pertanyaan umum seputar proses jual-beli, seperti pengiriman, cara pembelian, pembayaran, refund, retur, pembatalan, garansi, pelacakan pesanan, akun, promo, dan voucher. Contoh: `Bagaimana cara refund kalau barang rusak?`.

Jika user bertanya campuran, agent diarahkan untuk memakai kedua tool dan menggabungkan jawabannya.

## Struktur Project

```text
.
├── data/common_information.json
├── scripts/seed_common_information.py
├── src/smart_shopper/
│   ├── agent.py
│   ├── config.py
│   └── tools/
│       ├── common_information.py
│       └── product_recommendation.py
├── tests/
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## Setup

1. Buat virtual environment dan install dependency.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Buat file `.env` dari `.env.example`, lalu isi kredensial.

```env
GOOGLE_API_KEY=your_google_api_key
MONGODB_URI=your_mongodb_atlas_connection_string
MONGODB_DB_NAME=smart_shopper
MONGODB_COMMON_COLLECTION=common_information
MONGODB_VECTOR_INDEX=common_info_vector_index
EMBEDDING_MODEL=text-embedding-004
GENERATION_MODEL=gemini-2.0-flash
```

## Storing Data ke MongoDB Atlas

Dataset Common Information berada di `data/common_information.json`. Setiap item disimpan sebagai satu dokumen MongoDB dengan struktur:

- `title`: judul informasi.
- `category`: kategori seperti `shipping`, `refund`, atau `promo`.
- `question_examples`: contoh pertanyaan user.
- `content`: isi knowledge base.
- `source`: sumber dataset.
- `embedding`: vector embedding untuk Atlas Vector Search.
- `updated_at`: waktu penyimpanan terakhir.

Jalankan seed script:

```bash
python scripts/seed_common_information.py
```

Script akan membuat embedding untuk setiap dokumen, melakukan upsert berdasarkan `title` dan `category`, lalu mencetak definisi index Atlas Vector Search. Buat index tersebut di MongoDB Atlas dengan nama yang sama seperti `MONGODB_VECTOR_INDEX`.

Contoh bentuk index yang dicetak:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "category"
    }
  ]
}
```

Nilai `numDimensions` mengikuti output model embedding yang digunakan.

## Tools

### Product Recommendation

Function tool: `recommend_products(query: str)`

Tool ini memakai katalog lokal untuk demo. Output berisi produk yang direkomendasikan, kategori, harga, alasan rekomendasi, budget yang terdeteksi, dan saran pembelian.

### Common Information RAG

Function tool: `retrieve_common_information(query: str)`

Alur RAG:

1. Query user diubah menjadi embedding.
2. MongoDB Atlas `$vectorSearch` mengambil dokumen Common Information paling relevan.
3. Dokumen hasil retrieval diberikan ke model generatif.
4. Tool mengembalikan jawaban, kategori, dan sumber dokumen.

Jika konfigurasi belum lengkap, tool mengembalikan status `configuration_required`. Jika hasil retrieval lemah, tool menjawab bahwa informasi belum tersedia di knowledge base.

## Menjalankan Agent

Agent utama ada di `src/smart_shopper/agent.py` dengan variable `root_agent`. Untuk menjalankan melalui ADK CLI:

```bash
adk run smart_shopper
```

Jika ADK CLI membutuhkan path eksplisit di environment lokal, jalankan dari root project setelah dependency terinstall dan pastikan `src` terbaca sebagai source package.

## Routing Agent

Agent menggunakan dua tool langsung:

```python
tools=[recommend_products, retrieve_common_information]
```

Prompt agent mengatur routing:

- Product Recommendation untuk pertanyaan produk, spesifikasi, budget, kategori, dan rekomendasi.
- Common Information untuk pengiriman, pembelian, pembayaran, refund, retur, pembatalan, garansi, tracking, akun, promo, dan voucher.
- Pertanyaan campuran memakai kedua tool.

## Pengujian Manual

Gunakan prompt berikut untuk validasi:

- `Rekomendasikan headphone untuk meeting di bawah 500 ribu.`
- `Bagaimana cara refund kalau barang rusak?`
- `Berapa lama pengiriman reguler?`
- `Saya mau beli powerbank, kalau barangnya tidak cocok bisa retur?`

Ekspektasi:

- Pertanyaan produk memanggil `recommend_products`.
- Pertanyaan umum memanggil `retrieve_common_information`.
- Pertanyaan campuran memanggil kedua tool.
- Jawaban tetap dalam Bahasa Indonesia dan tidak mengarang informasi di luar context tool.

## Test

Test lokal tidak membutuhkan MongoDB Atlas atau Google API key.

```bash
pytest
```

Test mencakup validasi schema dataset, rekomendasi produk berbasis budget/kategori, dan respons konfigurasi Common Information ketika `.env` belum diisi.
