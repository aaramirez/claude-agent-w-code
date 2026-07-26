---
description: Generate a detailed requirements plan in plans/ before implementing anything
argument-hint: <feature description>
---

Create a detailed implementation plan for: $ARGUMENTS

## Process

1. **Understand** — analyze the request, identify all requirements and edge cases
2. **Research** — search the codebase for relevant files, patterns, and dependencies; use Context7 to fetch current documentation for any libraries/frameworks involved
3. **Plan document** — create `plans/<auto-number>-<feature-slug>-<YYYY-MM-DD>.md` with:
   - Objective (1 sentence)
   - Requirements (numbered list, prioritized)
   - Library/framework docs (from Context7, with version-specific API details)
   - File changes (new files, modified files, with paths)
   - TDD flow (tests first, then implementation)
   - Verification steps (how to confirm it works)
4. **Stop and wait for approval** — do not write tests or code until the user reviews the plan and explicitly asks to proceed

## Plan File Naming

Auto-number is the next sequential number in `plans/`. Date is today's date.

```
plans/001-feature-slug-2026-07-18.md
plans/002-another-feature-2026-07-19.md
```

## Plan Document Format

```markdown
# <Feature Name>

## Objective
[1 sentence]

## Requirements
1. [requirement] — priority: high/medium/low
2. ...

## Architecture
- Files to create: ...
- Files to modify: ...
- Decisions: ...

## TDD Flow
1. Write tests → FAIL
2. Implement → PASS
3. Refactor → still PASS

## Library/Dependencies
- Libraries used: [list libraries with Context7 doc references]
- Version-specific notes: [any API differences or breaking changes found]

## Verification
- [ ] Tests pass
- [ ] CI validation passes
- [ ] Documentation updated
```

## Rules
- Always create the plan document BEFORE writing any code
- Tests MUST fail before implementation (red-green-refactor)
- Update relevant docs (README/CLAUDE.md) if adding new agents/skills/scripts
- Do not execute the plan (write tests or code) unless the user explicitly says to proceed