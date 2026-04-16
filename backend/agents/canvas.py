"""StudyPilot LangGraph agent with Canvas MCP tools."""

import asyncio
import json

from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langsmith import traceable
from openai import AsyncOpenAI

from config import settings
from rag.retrieve import retrieve

_openai = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are StudyPilot, an AI study assistant with access to the student's Canvas LMS.

You can look up their courses and upcoming assignments via Canvas, and search their course syllabi and documents. When answering:
- Be concise and specific — students are busy.
- Always include due dates when discussing assignments.
- If asked something you can't answer with the available tools, say so clearly.
- Do not do the assignment for students, but help them understand what they need to do.
- You are here to assist them in learing, not to do their work for them.
"""

@traceable(name="eval-helpfulness", run_type="llm")
async def _eval_helpfulness(question: str, answer: str) -> dict:
    resp = await _openai.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evaluator. Rate how helpful the assistant's answer is "
                    "to a student's question on a scale of 1-5. "
                    "Respond with JSON: {\"score\": <int>, \"reasoning\": <str>}"
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nAnswer: {answer}",
            },
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


@tool
def search_documents(query: str) -> str:
    """Search the student's course syllabi and documents for relevant information.

    Use this when the student asks about course policies, grading, schedules,
    or any question that might be answered by course materials.
    """
    results = retrieve(query)
    if not results:
        return "No relevant documents found."
    return "\n\n---\n\n".join(
        f"[{r['source']}]\n{r['text']}" for r in results
    )


def _mcp_config() -> dict:
    return {
        "canvas": {
            "url": settings.canvas_mcp_url,
            "transport": "sse",
        }
    }


async def stream_agent(message: str, history: list[dict]):
    """Stream token chunks from the agent. Yields string chunks as they arrive."""
    client = MultiServerMCPClient(_mcp_config())
    tools = [*await client.get_tools(), search_documents]
    model = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        streaming=True,
    )
    agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)

    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ] + [{"role": "user", "content": message}]

    tool_labels = {t.name: t.description.splitlines()[0] for t in tools}
    full_response = ""

    async for event in agent.astream_events({"messages": messages}, version="v2"):
        kind = event["event"]
        node = event["metadata"].get("langgraph_node")

        if kind == "on_tool_start" and node == "tools":
            name = event["name"]
            label = tool_labels.get(name, name)
            yield f"__status__{label}__\n"

        elif kind == "on_chat_model_stream" and node == "agent":
            chunk = event["data"]["chunk"]
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

    if full_response:
        asyncio.ensure_future(_eval_helpfulness(question=message, answer=full_response))
