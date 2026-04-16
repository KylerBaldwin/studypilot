FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV MCP_TRANSPORT=sse

WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-install-project

COPY . .

EXPOSE 8001

CMD ["uv", "run", "python", "server.py"]
