---
name: code-review
description: Reviews code changes for bugs, style issues, and best practices. Use when reviewing PRs or checking code quality.
---

# Code Review

## When to Use This Skill

- User asks for a code review of recent changes.
- User wants feedback on code quality, correctness, or style.
- User is preparing a PR and wants a pre-review check.

## Goal

Review code changes with a focus on:

1. **Correctness**: Does the code do what it's supposed to?
2. **Edge cases**: Are error conditions handled?
3. **Style**: Does it follow project conventions?
4. **Performance**: Are there obvious inefficiencies?

## Workflow (Agent Instructions)

Prefer reviewing the actual diff (what changed) rather than only reading current file contents.

### 1 Determine review scope

1. Identify what you are reviewing:
  - Local working tree changes, or
  - A branch/PR compared to a base branch.
2. For local changes, start with:
  - `git status --porcelain`
3. For branch/PR-style review, pick a base branch (try `main` then `master`) and use:
  - `git diff <base>...HEAD --stat`
  - `git diff <base>...HEAD`

### 2 Summarize what changed

1. Run:

  - `git diff --stat`
  - `git diff --cached --stat`
2. Provide a 3–6 bullet summary of the intent of the changes.

### 3 Review checklist (apply to the diff)

#### Correctness

- Look for logic errors, incorrect assumptions, and mismatched units/types.
- Validate function contracts: inputs/outputs, return types, side effects.
- Check that refactors preserve behavior (renames, moved code, split functions).

#### Edge cases

- Null/empty input handling.
- File/path handling (prefer `pathlib` in this repo).
- Time-series/data issues: missing timestamps, empty DataFrames, NaNs.
- Defensive behavior: informative errors, safe fallbacks.

#### Style / Conventions

- PEP 8 formatting and readable naming.
- Prefer small, composable functions.
- Type hints when practical.
- Keep analysis logic aligned with existing conventions (7-day/30-day, 3-day comparisons).
- For CLI output, prefer existing `rich` patterns.

#### Performance

- Identify obvious pandas anti-patterns (row-wise `.apply` when vectorization works, repeated groupby/merge in loops).
- Avoid repeated file reads; prefer loading once and passing DataFrames through.
- Watch for N^2 operations on large datasets.

### 4 Scan for common foot-guns

Use diff + grep/search tools available in your shell/editor to flag:

- `breakpoint(`, `pdb`, `print(` (unless clearly intentional)
- `TODO` / `FIXME`
- commented-out blocks added

Examples (PowerShell):

- `git diff | Select-String -Pattern "breakpoint\(|print\(|TODO|FIXME"`
- `git diff --cached | Select-String -Pattern "breakpoint\(|print\(|TODO|FIXME"`

### 5 Basic validation

1. Run unit tests:
  - `uv run pytest`
3. If tests fail, report the failing tests and key traceback lines.

## How to Provide Feedback

- Be specific about what needs to change.
- Explain **why**, not just **what**.
- Suggest alternatives when possible.
- Distinguish **blocking** issues (bugs, crashes, wrong results) from **non-blocking** improvements (style, minor refactors).

## Output Template

```
CODE REVIEW

Summary:
- ...

Blocking Issues:
- ...

Non-blocking Suggestions:
- ...

Risk / Notes:
- ...

Validation:
- Diff reviewed: (staged/unstaged or <base>...HEAD)
- Tests: PASS/FAIL (details)

Recommendation: APPROVE / REQUEST CHANGES
```
