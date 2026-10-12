# Personalized SmartShopper Assistant

An AI agent for e-commerce built with Google ADK. It routes each customer question to the right tool: a product recommendation tool, and a Common Information tool that answers policy questions with RAG over MongoDB Atlas Vector Search. The agent answers in Indonesian.

## How routing works

**Product questions** need a recommendation, search, comparison, category, specs, budget or fit. Example: `Rekomendasikan headphone untuk meeting di bawah 500 ribu` ("Recommend headphones for meetings under 500k").

**Common information questions** are about the buying process: shipping, how to buy, payment, refunds, returns, cancellations, warranty, order tracking, accounts, promos and vouchers. Example: `Bagaimana cara refund kalau barang rusak?` ("How do I get a refund if the item is damaged?").

Mixed questions use both tools and combine the answers. The agent has two tools:

```python
tools=[recommend_products, retrieve_common_information]
```

## Tools

### Product recommendation: `recommend_products(query: str)`

Uses a local demo catalogue. Returns recommended products, category, price, the reason for each recommendation, the detected budget and buying advice.

### Common Information RAG: `retrieve_common_information(query: str)`

1. Embed the user's query.
2. Retrieve the most relevant documents with MongoDB Atlas `$vectorSearch`.
3. Pass the retrieved documents to the generative model.
4. Return the answer, category and source documents.

If configuration is missing, the tool returns `configuration_required`. If retrieval is weak, it says the information isn't in the knowledge base rather than guessing.

## Project structure

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

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and fill in your credentials:

```env
GOOGLE_API_KEY=your_google_api_key
MONGODB_URI=your_mongodb_atlas_connection_string
MONGODB_DB_NAME=smart_shopper
MONGODB_COMMON_COLLECTION=common_information
MONGODB_VECTOR_INDEX=common_info_vector_index
EMBEDDING_MODEL=text-embedding-004
GENERATION_MODEL=gemini-2.0-flash
```

## Storing data in MongoDB Atlas

The Common Information dataset is in `data/common_information.json`. Each item is stored as one MongoDB document with `title`, `category` (such as `shipping`, `refund` or `promo`), `question_examples`, `content`, `source`, `embedding` and `updated_at`.

Run the seed script:

```bash
python scripts/seed_common_information.py
```

It embeds every document, upserts by `title` and `category`, and prints the Atlas Vector Search index definition. Create that index in MongoDB Atlas with the same name as `MONGODB_VECTOR_INDEX`. Example output:

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

`numDimensions` follows the embedding model's output size.

## Running the agent

The main agent is `root_agent` in `src/smart_shopper/agent.py`. Run it with the ADK CLI:

```bash
adk run smart_shopper
```

If the ADK CLI needs an explicit path locally, run it from the project root after installing dependencies and make sure `src` is importable as a source package.

## Manual testing

Try these prompts:

- `Rekomendasikan headphone untuk meeting di bawah 500 ribu.` (product)
- `Bagaimana cara refund kalau barang rusak?` (common information)
- `Berapa lama pengiriman reguler?` (common information: regular shipping time)
- `Saya mau beli powerbank, kalau barangnya tidak cocok bisa retur?` (mixed: buy a power bank, can I return it?)

Expected: product questions call `recommend_products`, general questions call `retrieve_common_information`, mixed questions call both, and answers stay in Indonesian without inventing information outside the tool context.

## Tests

The local tests don't need MongoDB Atlas or a Google API key.

```bash
pytest
```

They cover dataset schema validation, budget- and category-based recommendations, and the Common Information configuration response when `.env` is empty.
