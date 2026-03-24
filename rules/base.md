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
- Write the test cases from the spec FIRST as a test file
- Then implement the code to make those tests pass
- Do not mark a story complete if any test fails

### Spec is the source of truth
- If your implementation conflicts with the spec, fix the implementation
- If you think the spec is wrong, state it explicitly and wait — do not silently deviate
- Comments in code should reference the spec requirement they satisfy
  e.g. # FR-1: filter out seats_available == 0 per spec

### Definition of done
A story is only complete when:
- [ ] All functions exist with the exact signatures from the spec
- [ ] All acceptance criteria are checked off
- [ ] All manual tests from the spec pass
- [ ] No extra files or functions were created outside the spec
- [ ] Code has been linted with no errors (ruff check .)