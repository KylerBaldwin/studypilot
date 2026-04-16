import httpx
from datetime import datetime, timezone
from html.parser import HTMLParser

# Canvas API helper functions

async def _request(client: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response:
    """GET, raising a clear error on Canvas 429 rate limit."""
    r = await client.get(url, params=params)
    if r.status_code == 429:
        raise RuntimeError("Canvas API rate limit reached. Please try again in a moment.")
    r.raise_for_status()
    return r


async def _get_current_term_id(client: httpx.AsyncClient) -> int | None:
    """Return the enrollment_term_id whose date range contains today.

    Falls back to None if the account endpoint is forbidden (common for
    student tokens at some institutions).
    """
    try:
        r = await _request(client, "/accounts/self/terms")
        terms = r.json().get("enrollment_terms", [])
        now = datetime.now(timezone.utc)
        for term in terms:
            start = term.get("start_at")
            end = term.get("end_at")
            if start and end:
                s = datetime.fromisoformat(start.replace("Z", "+00:00"))
                e = datetime.fromisoformat(end.replace("Z", "+00:00"))
                if s <= now <= e:
                    return term["id"]
    except httpx.HTTPError:
        pass
    return None


async def _paginate(client: httpx.AsyncClient, path: str, params: dict) -> list:
    """GET a paginated Canvas endpoint, following Link: rel=next until done."""
    results = []
    url = path
    while url:
        r = await _request(client, url, params)
        results.extend(r.json())
        params = {}  # params are encoded in the next URL already
        next_link = None
        for part in r.headers.get("link", "").split(","):
            if 'rel="next"' in part:
                next_link = part.split(";")[0].strip().strip("<>")
                # strip the base URL prefix so we pass a relative path
                base = str(client.base_url).rstrip("/")
                next_link = next_link.replace(base, "")
        url = next_link
    return results

# HTML helper functions

class _StripHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
    def handle_data(self, data: str) -> None:
        self._parts.append(data)
    def get_text(self) -> str:
        return " ".join(self._parts).strip()

def _strip_html(html: str | None) -> str:
    if not html:
        return ""
    parser = _StripHTML()
    parser.feed(html)
    return parser.get_text()

def _shape_assignment(a: dict) -> dict:
    return {
        "id": a["id"],
        "name": a["name"],
        "course_id": a["course_id"],
        "due_at": a.get("due_at"),
        "lock_at": a.get("lock_at"),
        "points_possible": a.get("points_possible"),
        "submitted": a.get("has_submitted_submissions", False),
        "bucket": a.get("bucket"),
        "description": _strip_html(a.get("description")),
    }