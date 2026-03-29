---
sprint: sprint-1
theme: MCP Tools + Agent Core
start: 2026-03-16
end: 2026-03-21
status: done
---

# Sprint 1 — MCP Tools + Agent Core

## Dates
Start: 2026-03-16
End:   2026-03-21

## Goal
Build and test all 4 MCP search tools, the Claude agent loop, per-user memory, and the package builder formatter.

## Stories

| Ticket | Title | Status |
|--------|-------|--------|
| TB-01  | MCP Server — Search Flights | [x] done |
| TB-02  | MCP Server — Search Hotels | [x] done |
| TB-03  | MCP Server — Search Activities | [x] done |
| TB-04  | MCP Server — Search Transport | [x] done |
| TB-05  | Agent Core — Tool Calling Loop | [x] done |
| TB-06  | Memory — Per-User Conversation History | [x] done |
| TB-07  | Package Builder — Format Tour Package | [x] done |

## Definition of Done
- [x] All stories complete and tests passing
- [x] No ruff lint errors
- [x] Manual smoke test against running server passes

## Notes / Blockers
Transport test coverage (TB-04) was deferred and completed in TB-11 (Sprint 2).
Package builder interface was corrected in TB-12 (Sprint 2).
