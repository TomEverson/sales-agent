import json
import os
from pathlib import Path
from typing import Any

import anthropic
import httpx

from memory import get_history, append_message
from mcp_tools import TOOLS, execute_tool

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 4096

_system_prompt: str | None = None


def _load_system_prompt() -> str:
    global _system_prompt
    if _system_prompt is None:
        path = Path(__file__).parent / "prompts" / "system_prompt.md"
        _system_prompt = path.read_text(encoding="utf-8")
    return _system_prompt


def _get_client() -> anthropic.AsyncAnthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return anthropic.AsyncAnthropic(api_key=api_key)


async def handle_message(user_id: int, user_text: str) -> str:
    """
    Process a user message through the agentic tool-calling loop.
    Returns the final text response from Claude.
    """
    # Append the new user message to history
    append_message(user_id, {"role": "user", "content": user_text})

    client = _get_client()
    system_prompt = _load_system_prompt()

    try:
        response_text = await _run_agent_loop(client, system_prompt, user_id)
    except httpx.ConnectError:
        response_text = (
            "Sorry, I can't reach the Travelbase inventory right now. "
            "Please try again in a moment."
        )
    except Exception as e:
        response_text = f"Something went wrong: {e}. Please try again."

    # Append the final assistant reply to history
    append_message(user_id, {"role": "assistant", "content": response_text})
    return response_text


async def _run_agent_loop(
    client: anthropic.AsyncAnthropic,
    system_prompt: str,
    user_id: int,
) -> str:
    """
    Agentic loop: call Claude, execute any tool_use blocks, feed results back,
    repeat until Claude returns a pure text response.
    """
    # We maintain a local messages list that mirrors the stored history
    # but may include in-flight tool_use / tool_result turns not yet persisted.
    messages: list[dict[str, Any]] = list(get_history(user_id))

    while True:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        # Collect all content blocks from this response
        assistant_content: list[dict[str, Any]] = []
        tool_use_blocks: list[Any] = []

        for block in response.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
                tool_use_blocks.append(block)

        # Append the assistant turn (may contain tool_use blocks)
        messages.append({"role": "assistant", "content": assistant_content})

        # If no tool calls, we're done — extract the text response
        if not tool_use_blocks:
            for block in assistant_content:
                if block["type"] == "text":
                    return block["text"]
            return "I couldn't generate a response. Please try again."

        # Execute all tool calls and collect results
        tool_results: list[dict[str, Any]] = []
        for block in tool_use_blocks:
            try:
                result = await execute_tool(block.name, block.input)
                # execute_tool returns a str (JSON or error message) — use directly
                result_content = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
            except Exception as exc:
                result_content = json.dumps({"error": str(exc)})

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_content,
            })

        # Append tool results as a user turn and loop
        messages.append({"role": "user", "content": tool_results})
