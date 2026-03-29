# Specs

This folder is the source of truth for all planned and completed work on Travelbase Salebot.
Every feature, fix, and chore starts here as a spec before any code is written.

---

## Folder Structure

```
specs/
├── README.md                  ← you are here
├── DEFINITION_OF_DONE.md      ← shared DoD referenced by all tickets
├── _templates/
│   ├── feature.md             ← template for new tickets
│   └── sprint.md              ← template for new sprints
├── backlog/                   ← drafted tickets not yet assigned to a sprint
│   └── tb-XX-<type>-<title>.md
├── sprint-1/
│   ├── sprint.md              ← sprint goal, stories, status
│   └── tb-XX-<type>-<title>.md
├── sprint-2/
│   └── ...
└── sprint-3/
    └── ...
```

---

## Ticket Naming Convention

```
tb-<number>-<type>-<short-title>.md
```

| Part | Description | Example |
|------|-------------|---------|
| `tb` | Project prefix — Travelbase | `tb` |
| `<number>` | Two-digit sequential number | `01`, `12` |
| `<type>` | Ticket type (see below) | `feat` |
| `<short-title>` | Kebab-case description | `search-flights` |

**Full example:** `tb-01-feat-search-flights.md`

### Ticket Types

| Type | When to use |
|------|-------------|
| `feat` | New user-facing functionality |
| `fix` | Bug fix or incorrect behaviour |
| `chore` | Refactor, cleanup, test coverage, dependencies |
| `test` | Adding tests for already-shipped code with no coverage |

---

## How to Write a New Ticket

1. Copy `_templates/feature.md`
2. Name it `tb-<next-number>-<type>-<title>.md` and place it in `backlog/`
3. Fill in all sections — do not leave Goal or Acceptance Criteria blank
4. Assign to a sprint when sprint planning begins (move file to `sprint-N/`)

**Never start coding without a ticket. Never mark a ticket done with failing tests.**

---

## How Sprints Work

Each sprint folder contains:
- `sprint.md` — goal, story list, dates, status, notes
- One file per ticket assigned to that sprint

Sprint statuses: `planned` → `in-progress` → `done`

Update `sprint.md` status as you go. When all tickets in a sprint are done, mark the sprint done.

---

## Ticket Lifecycle

```
backlog/ → sprint-N/ → [in-progress] → [done]
```

A ticket is **done** only when:
- All acceptance criteria are checked off
- All tests pass: `uv run pytest tests/ -v`
- Lint is clean: `uv run ruff check .`
- PR is merged (if applicable)

---

## Current Sprints

| Sprint | Theme | Dates | Status |
|--------|-------|-------|--------|
| sprint-1 | MCP Tools + Agent Core | Mar 16 – Mar 21 | done |
| sprint-2 | Bot Integration + Fixes | Mar 22 – Mar 27 | done |
| sprint-3 | TBD | Mar 28 – Apr 3 | planned |
