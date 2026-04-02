import os
from pathlib import Path
from typing import Any

import anthropic

from mcp_tools import TOOLS, execute_tool

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 4096

_system_prompt: str | None = None
_prompt_cache: dict[str, str] = {}

_FALLBACK_PROMPT = "You are Travelbase Assistant, a helpful travel sales agent."


def load_system_prompt(lang: str = "en") -> str:
    if lang not in _prompt_cache:
        try:
            filename = "system_prompt.md" if lang == "en" else "system_prompt_my.md"
            path = Path(__file__).parent / "prompts" / filename
            _prompt_cache[lang] = path.read_text(encoding="utf-8")
        except Exception:
            _prompt_cache[lang] = _FALLBACK_PROMPT
    return _prompt_cache[lang]


async def execute_tool_call(tool_name: str, tool_input: dict) -> str:
    try:
        return await execute_tool(tool_name, tool_input)
    except Exception as e:
        return f"Tool {tool_name} failed with error: {str(e)}"


async def run_agent(
    user_id: int, user_message: str, history: list, lang: str = "en"
) -> str:
    messages: list[dict[str, Any]] = list(history) + [
        {"role": "user", "content": user_message}
    ]
    client = _get_client()
    system = load_system_prompt(lang)

    for _ in range(10):
        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "I have no response. Please try again."

        if response.stop_reason == "tool_use":
            # FR-13: serialise content blocks to plain dicts before appending
            assistant_content: list[dict[str, Any]] = []
            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results: list[dict[str, Any]] = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await execute_tool_call(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        return "I encountered an unexpected error. Please try again."

    return "I was unable to complete your request in time. Please try again."


def _get_client() -> anthropic.AsyncAnthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return anthropic.AsyncAnthropic(api_key=api_key)
