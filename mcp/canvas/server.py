"""Canvas MCP server — exposes get_courses and get_assignments as MCP tools."""

import asyncio
import json
import os

import httpx
from fastmcp import FastMCP

from utils import _get_current_term_id, _shape_assignment, _paginate

CANVAS_TOKEN = os.environ["CANVAS_TOKEN"]
CANVAS_BASE_URL = os.environ.get("CANVAS_BASE_URL", "https://canvas.instructure.com")
BASE = f"{CANVAS_BASE_URL}/api/v1"
HEADERS = {"Authorization": f"Bearer {CANVAS_TOKEN}"}

def _make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE, headers=HEADERS, timeout=15)

mcp = FastMCP("canvas")

@mcp.tool()
async def get_courses() -> str:
    """List the student's active enrolled courses for the current term.

    Returns a JSON array with id, name, course_code, start_at, end_at.
    """
    async with _make_client() as client:
        term_id = await _get_current_term_id(client)
        params: dict = {
            "enrollment_state": "active",
            "enrollment_type": "student",
            "per_page": 50,
        }
        if term_id:
            params["enrollment_term_id"] = term_id

        courses = await _paginate(client, "/courses", params)

    filtered = [
        {
            "id": c["id"],
            "name": c["name"],
            "course_code": c["course_code"],
            "start_at": c.get("start_at"),
            "end_at": c.get("end_at"),
        }
        for c in courses
        if c.get("end_at")
    ]
    return json.dumps(filtered, indent=2)


@mcp.tool()
async def get_assignments(course_id: str | None = None) -> str:
    """Get upcoming assignments for a course.

    Args:
        course_id: The numeric Canvas course ID (e.g. "123456") from get_courses.
                   NOT the course code (e.g. "MSIS-5663"). If omitted, fetches
                   upcoming assignments across all active courses concurrently.

    Returns a JSON array sorted by effective due date (due_at, then lock_at).
    """
    async with _make_client() as client:
        if course_id:
            raw = await _paginate(
                client,
                f"/courses/{course_id}/assignments",
                {"order_by": "due_at", "bucket": "future", "per_page": 50},
            )
        else:
            term_id = await _get_current_term_id(client)
            params: dict = {
                "enrollment_state": "active",
                "enrollment_type": "student",
                "per_page": 50,
            }
            if term_id:
                params["enrollment_term_id"] = term_id

            courses = [
                c for c in await _paginate(client, "/courses", params)
                if c.get("end_at")
            ]

            results = await asyncio.gather(*[
                _paginate(
                    client,
                    f"/courses/{c['id']}/assignments",
                    {"order_by": "due_at", "bucket": "future", "per_page": 50},
                )
                for c in courses
            ])
            raw = [a for course_assignments in results for a in course_assignments]

    shaped = [_shape_assignment(a) for a in raw]
    shaped.sort(key=lambda a: (a["due_at"] or a["lock_at"] or "9999"))
    return json.dumps(shaped, indent=2)


if __name__ == "__main__":
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport, host="0.0.0.0", port=8001)