# 🔍 Repo Intelligence Engine

Advanced repository intelligence analysis and AI architectural review powered by Hugging Face Inference API.

## Features

- **Multi-Language Parsing** — Python (AST), JavaScript/TypeScript (regex), JSX/TSX (React component detection), Java, Go, C#, C++, PHP
- **Dependency Analysis** — `package.json`, `requirements.txt`, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`
- **Architecture Diagrams** — Module dependency graph, API route flow, React component relationship graph (Graphviz)
- **Framework Detection** — Next.js, Vite, Express, FastAPI, Django, Flask, Angular, Vue, and more
- **Infrastructure Detection** — Docker, CI/CD pipelines
- **AI Architectural Review** — Powered by Mistral-7B-Instruct via Hugging Face Inference API

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** You also need [Graphviz](https://graphviz.org/download/) installed on your system for architecture diagrams. On Ubuntu: `sudo apt install graphviz`. On macOS: `brew install graphviz`. On Windows: download from the Graphviz website and add to PATH.

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Open in Browser

Navigate to `http://localhost:8501`

## Configuration

### GitHub Token (Optional, Recommended)

Without a token, GitHub API is limited to 60 requests/hour. With a token, the limit is 5,000/hour.

Set via environment variable:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Or add to `.streamlit/secrets.toml`:

```toml
GITHUB_TOKEN = "ghp_your_token_here"
```

### Hugging Face API Token (Required for AI Review)

Get a free token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

Set via environment variable:

```bash
export HF_API_TOKEN=hf_your_token_here
```

Or add to `.streamlit/secrets.toml`:

```toml
HF_API_TOKEN = "hf_your_token_here"
```

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"** and select your repository.
4. Set the main file path to `app.py`.
5. Go to **Advanced settings > Secrets** and add:

```toml
GITHUB_TOKEN = "ghp_your_token_here"
HF_API_TOKEN = "hf_your_token_here"
```

6. Click **Deploy**.

## Project Structure

```
repo_intelligence/
├── app.py               # Streamlit web application
├── github_fetcher.py    # GitHub REST API integration
├── file_classifier.py   # File type classification engine
├── static_parser.py     # Multi-language static code analysis
├── config_parser.py     # Configuration file parser
├── graph_builder.py     # Graphviz architecture diagram generator
├── ai_interpreter.py    # Hugging Face AI interpretation layer
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## How It Works

1. **Fetch** — Recursively fetches the repository tree via GitHub REST API (`GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1`)
2. **Classify** — Categorizes files into source, config, documentation, and assets
3. **Parse** — Extracts classes, functions, components, imports, routes, and dependencies
4. **Graph** — Builds architecture diagrams using Graphviz
5. **Analyze** — Sends structured JSON (never raw code) to Mistral-7B for architectural review

## Limits

| Limit | Value |
|-------|-------|
| Max files processed | 100 |
| Max file size | 200 KB |
| Skipped directories | `node_modules`, `.git`, `dist`, `build`, `.next`, `coverage`, `__pycache__`, `venv` |

## License

MIT
