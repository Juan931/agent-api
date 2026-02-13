## v1 – Initial local agent API

- FastAPI backend to interact with a local LLM via Ollama.
- Dockerized setup for running the API locally using an `env.list` file.
- /health endpoint to check service status.
- Returns 503 with a JSON `detail` when Ollama is unreachable instead of crashing.
