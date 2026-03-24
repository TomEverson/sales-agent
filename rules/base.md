# Travelbase Salebot — Base Rules

You are building P.02 Travelbase Salebot — an AI-powered tour package sales agent.

## Reference Files
- rules/base.md     → Current File
- rules/server.md   → FastAPI backend (already built)
- rules/client.md   → React frontend (already built)
- rules/bot.md      → Telegram bot agent (already built)

Do NOT rebuild anything already in those files.
Implement only the story assigned to you.

---

## Development Rules
- Implement one story at a time
- Each story must be fully working before moving to the next
- After each story, print: "✅ FR-X complete"
- Never skip acceptance criteria
- If a story depends on a previous one, say so and stop

---

## Spec-Driven Development Rules

### Before writing any code
- Read the full story spec before touching any file
- Identify every function, input, output, and edge case described in the spec
- If the spec is ambiguous, state your assumption explicitly before proceeding
- Do not invent behavior that is not in the spec

### Writing code
- Every function must match the signature defined in the spec exactly
  (name, parameters, return type)
- Every constant, variable name, and file path must match the spec exactly
- Do not add extra features, helpers, or abstractions not described in the spec
- Do not rename things because you prefer a different style

### Tests come before implementation
- Create the test file FIRST before writing any implementation code
- Test file must be created at: salebot/tests/test_<module_name>.py
- Write all test cases derived from the spec's acceptance criteria and manual tests
- Use pytest and pytest-asyncio for all tests
- Only after the test file exists, write the implementation to make tests pass
- Do not mark a story complete if any test fails

### Test folder structure
Every story must produce a test file in this structure:
```
salebot/
└── tests/
    ├── __init__.py            ← create once, never overwrite
    ├── conftest.py            ← shared fixtures (create once, append per story)
    ├── test_mcp_tools.py      ← FR-1, FR-2, FR-3, FR-4
    ├── test_agent.py          ← FR-5
    ├── test_memory.py         ← FR-6
    ├── test_package_builder.py ← FR-7
    └── test_bot.py            ← FR-9
```

### Test file rules
- Each test function name must match the acceptance criterion it covers
  e.g. test_search_flights_filters_out_zero_seats()
- Each test must have a one-line docstring referencing the spec
  e.g. """FR-1: seats_available == 0 must be filtered out per spec"""
- Use pytest.mark.asyncio for all async tests
- Mock all HTTP calls using pytest-mock or respx — never call the real FastAPI in tests
- Group tests by function using a class per function
  e.g. class TestExecuteSearchFlights:
- Every edge case in the spec must have its own test function

### conftest.py rules
- Add shared fixtures here, never duplicate them across test files
- Each story appends its own fixtures — do not remove existing ones
- Common fixtures to define once:
  - mock_flight_response → returns a list of sample flight dicts
  - mock_hotel_response → returns a list of sample hotel dicts
  - mock_activity_response → returns a list of sample activity dicts
  - mock_transport_response → returns a list of sample transport dicts

### Running tests
- Install test dependencies: uv add --dev pytest pytest-asyncio respx
- Run all tests: uv run pytest tests/ -v
- Run one story's tests: uv run pytest tests/test_mcp_tools.py -v
- All tests must pass before story is marked done

### Spec is the source of truth
- If your implementation conflicts with the spec, fix the implementation
- If you think the spec is wrong, state it explicitly and wait — do not silently deviate
- Comments in code should reference the spec requirement they satisfy
  e.g. # FR-1: filter out seats_available == 0 per spec

### Definition of done
A story is only complete when:
- [ ] Test file exists at the correct path
- [ ] All test functions are named after their acceptance criteria
- [ ] All tests pass: uv run pytest tests/ -v
- [ ] All functions exist with the exact signatures from the spec
- [ ] All acceptance criteria are checked off
- [ ] No extra files or functions were created outside the spec
- [ ] Code has been linted with no errors: uv run ruff check .