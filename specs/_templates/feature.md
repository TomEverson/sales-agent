---
ticket: TB-XX
type: feat | fix | chore | test
title: <Short Title>
sprint: sprint-N
status: todo | in-progress | done
component: salebot | server | client
depends_on: TB-XX | none
---

# TB-XX: <Title>

> **Filename:** `tb-XX-<type>-<short-title>.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-XX (or "none")
- Sprint: sprint-N
- Component: salebot | server | client

## Goal
One paragraph — what problem does this solve?

## Files to create / modify
- `path/to/file.py` ← create | modify

## What to build
### 1. <Section>
...

## Acceptance Criteria
- [ ] criterion 1
- [ ] criterion 2

## Test file
`salebot/tests/test_<module>.py`

## Manual test
```python
# paste manual test script here
```

## Definition of Done
- [ ] Test file exists at correct path
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Linted: `uv run ruff check .`
- [ ] All acceptance criteria checked
