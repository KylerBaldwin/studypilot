# Canvas MCP Server

FastMCP server that exposes Canvas LMS data as tools for the StudyPilot agent.

## Tools

| Tool | Description |
|------|-------------|
| `get_courses` | Active enrolled courses for the current term (id, name, course_code, start_at, end_at) |
| `get_assignments` | Upcoming assignments sorted by due date. Optionally scoped to a single `course_id`, otherwise fetches across all current-term courses concurrently |

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CANVAS_TOKEN` | Yes | — | Canvas API token — Canvas > Account > Settings > New Access Token |
| `CANVAS_BASE_URL` | No | `https://canvas.instructure.com` | Your institution's Canvas domain |
| `MCP_TRANSPORT` | No | `stdio` | `stdio` for Claude Desktop, `sse` for HTTP server mode |

Copy `.env.example` to `.env` and fill in the values.

## Development

Requires [uv](https://docs.astral.sh/uv/) and [Doppler](https://docs.doppler.com/docs/cli) (or any env injector).

Install dependencies:

```bash
cd mcp/canvas
uv sync
```

Run the MCP Inspector to interactively call tools in the browser:

```bash
doppler run -- uv run fastmcp dev inspector server.py
```

## Transports

| Transport | Command | Use case |
|-----------|---------|----------|
| `stdio` | `uv run python server.py` | Claude Desktop, local MCP clients |
| `sse` | `MCP_TRANSPORT=sse uv run python server.py` | Docker / Railway, agent backends |

In Docker the transport is set to `sse` automatically via the `Dockerfile`.
