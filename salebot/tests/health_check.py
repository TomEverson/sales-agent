"""
FR-10: Health check script for Travelbase Salebot.
Requires:
  - FastAPI server running at http://localhost:8000
  - ANTHROPIC_API_KEY set in .env
Run with: uv run python tests/health_check.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def check_fastapi_reachable():
    """Check 1: FastAPI server is reachable"""
    import httpx
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("http://localhost:8000/")
        assert resp.status_code < 500


async def check_flights_endpoint():
    """Check 2: /flights returns at least 1 result"""
    import httpx
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("http://localhost:8000/flights")
        resp.raise_for_status()
        data = resp.json()
        assert len(data) >= 1


async def check_hotels_endpoint():
    """Check 3: /hotels returns at least 1 result"""
    import httpx
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("http://localhost:8000/hotels")
        resp.raise_for_status()
        data = resp.json()
        assert len(data) >= 1


async def check_activities_endpoint():
    """Check 4: /activities returns at least 1 result"""
    import httpx
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("http://localhost:8000/activities")
        resp.raise_for_status()
        data = resp.json()
        assert len(data) >= 1


async def check_transport_endpoint():
    """Check 5: /transport returns at least 1 result"""
    import httpx
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get("http://localhost:8000/transport")
        resp.raise_for_status()
        data = resp.json()
        assert len(data) >= 1


async def check_mcp_tools_importable():
    """Check 6: mcp_tools.py imports without error"""
    import mcp_tools
    assert hasattr(mcp_tools, "TOOLS")
    assert hasattr(mcp_tools, "execute_tool")


async def check_agent_importable():
    """Check 7: agent.py imports without error"""
    import agent
    assert hasattr(agent, "run_agent")
    assert hasattr(agent, "load_system_prompt")


async def check_memory_importable():
    """Check 8: memory.py imports without error"""
    import memory
    assert hasattr(memory, "get_history")
    assert hasattr(memory, "append_message")
    assert hasattr(memory, "clear_history")


async def check_package_builder_importable():
    """Check 9: package_builder.py imports without error"""
    import package_builder
    assert package_builder is not None


async def check_system_prompt_loaded():
    """Check 10: system_prompt.md loads and is not placeholder"""
    import agent
    agent._system_prompt = None  # reset cache
    prompt = agent.load_system_prompt()
    assert len(prompt) >= 1000, f"Prompt too short: {len(prompt)} chars"
    assert "Bangkok" in prompt, "Prompt missing Bangkok default"
    assert "NEVER" in prompt, "Prompt missing NEVER rules"


async def check_full_agent_run():
    """Check 11: run_agent produces a non-empty response for Singapore $1000 request"""
    from agent import run_agent
    result = await run_agent(
        user_id=0,
        user_message="I want to visit Singapore this weekend, my budget is $1000",
        history=[],
    )
    assert isinstance(result, str)
    assert len(result) > 0


async def run_all_checks():
    checks = [
        check_fastapi_reachable,
        check_flights_endpoint,
        check_hotels_endpoint,
        check_activities_endpoint,
        check_transport_endpoint,
        check_mcp_tools_importable,
        check_agent_importable,
        check_memory_importable,
        check_package_builder_importable,
        check_system_prompt_loaded,
        check_full_agent_run,
    ]

    passed = 0
    failed = 0

    print("\n🔍 Travelbase Salebot — Health Check\n")
    print("=" * 50)

    for check in checks:
        try:
            await check()
            print(f"  ✅ {check.__doc__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {check.__doc__}")
            print(f"     Error: {e}")
            failed += 1

    print("=" * 50)
    print(f"\nResult: {passed} passed, {failed} failed\n")

    if failed > 0:
        print("❌ Health check failed — fix errors above before running the bot.")
        sys.exit(1)
    else:
        print("✅ All checks passed — bot is ready to run.")
        print("   Start with: uv run python bot.py\n")


if __name__ == "__main__":
    asyncio.run(run_all_checks())
