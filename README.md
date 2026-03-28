# LinkedIn Post Generator

A small Streamlit app that generates LinkedIn-style posts by topic, length, and language. It uses [Groq](https://console.groq.com/) (via LangChain) with a few-shot layer: example posts are loaded from `data/processed_posts.json` and matched by tag, language, and length when available.

## Requirements

- Python **3.12+**
- A Groq API key

## Setup

Install dependencies with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The app uses `llama-3.3-70b-versatile` with temperature `0` (see `llm_helper.py`).

## Run the app

```bash
streamlit run main.py
```

Choose a **Topic** (from tags in the dataset), **Length** (Short / Medium / Long), and **Language** (English / Hinglish), then click **Generate**.

## Regenerate processed data (optional)

Example posts are stored as JSON. Raw posts live in `data/raw_posts.json`. To rebuild `data/processed_posts.json` (LLM-based tagging, language, line counts, and tag unification), run:

```bash
python preprocess.py
```

This calls the same Groq model and overwrites `data/processed_posts.json`.

## Project layout

| Path | Role |
|------|------|
| `main.py` | Streamlit UI |
| `post_generator.py` | Prompt construction and generation |
| `few_shot.py` | Load/filter examples from processed JSON |
| `llm_helper.py` | Shared `ChatGroq` client |
| `preprocess.py` | Raw → processed dataset pipeline |
| `data/raw_posts.json` | Source posts |
| `data/processed_posts.json` | Posts with `tags`, `language`, `line_count` for few-shot matching |

## License

Add a license if you publish this repo publicly.
