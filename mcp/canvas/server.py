"""Canvas MCP server — stdio transport. Spawn as a subprocess, pass CANVAS_TOKEN via env."""

import os
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

CANVAS_TOKEN = os.environ["CANVAS_TOKEN"]
CANVAS_BASE_URL = os.environ.get("CANVAS_BASE_URL", "https://canvas.instructure.com")

server = Server("canvas")
_client = httpx.Client(
    base_url=f"{CANVAS_BASE_URL}/api/v1",
    headers={"Authorization": f"Bearer {CANVAS_TOKEN}"},
    timeout=15,
)


def _get(path: str, params: dict | None = None) -> list | dict:
    r = _client.get(path, params=params)
    r.raise_for_status()
    return r.json()


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_courses",
            description="List enrolled courses with name, course code, and term.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_assignments",
            description="Upcoming assignments with due dates, points, and submission status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Optional course ID filter"}
                },
            },
        ),
        types.Tool(
            name="get_announcements",
            description="Recent course announcements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Optional course ID filter"}
                },
            },
        ),
        types.Tool(
            name="get_grades",
            description="Current grades per course.",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_id": {"type": "string", "description": "Optional course ID filter"}
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    course_id = arguments.get("course_id")

    if name == "get_courses":
        data = _get("/courses", {"enrollment_state": "active"})

    elif name == "get_assignments":
        path = f"/courses/{course_id}/assignments" if course_id else "/users/self/upcoming_events"
        data = _get(path, {"order_by": "due_at", "bucket": "upcoming"} if not course_id else {})

    elif name == "get_announcements":
        params = {"per_page": 10}
        if course_id:
            data = _get(f"/courses/{course_id}/discussion_topics", {**params, "only_announcements": True})
        else:
            data = _get("/announcements", params)

    elif name == "get_grades":
        if course_id:
            data = _get(f"/courses/{course_id}/enrollments", {"user_id": "self"})
        else:
            data = _get("/users/self/enrollments", {"type[]": "StudentEnrollment", "state[]": "active"})

    else:
        raise ValueError(f"Unknown tool: {name}")

    import json
    return [types.TextContent(type="text", text=json.dumps(data, indent=2))]


if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
