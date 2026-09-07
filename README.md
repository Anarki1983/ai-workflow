# ai-workflow

*[Traditional Chinese translation available: `README.zh-TW.md`]*

A personal execution-stage routing method, for any project built mainly on Claude Code + superpowers.

## What problem this repo solves

The home directory's `~/.claude/CLAUDE.md` already has a **decision-stage** rule: when a new requirement, new feature, or behavior change comes up, pick one of brainstorming / grill-with-docs / plan mode before moving forward. That rule solves "should we do this, and how."

What it doesn't solve is the **execution stage**: once the decision is made and you're actually about to touch the repo, which superpowers skill a given change should use (TDD? systematic-debugging? frontend-design?), which specialized agent to call, which check script to run afterward — this varies by project, is too vague for a home-directory rule, and is easy to forget or apply inconsistently if you have to think it through fresh each time.

`skills/change-type-routing/` fills that gap: not a pre-filled table, but a method for helping any project inventory its own table.

A second skill, `skills/team-review-pipeline/`, covers a different axis of the same execution stage: not *which* mechanism handles a change, but *how deep review goes* and *who is allowed to merge* on a team where AI leads most implementation. It doesn't invent new mechanisms — it composes existing superpowers skills into one pipeline: superpowers:test-driven-development and superpowers:verification-before-completion gate what "tests pass" is allowed to mean (the tests-only review default below only holds if tests were written test-first, with real verification output, not a claim); superpowers:using-git-worktrees isolates concurrent work; superpowers:writing-plans / executing-plans break large changes into one-PR-per-task; superpowers:finishing-a-development-branch handles cleanup after merge. Its review-depth exception list, multi-model-review trigger, and 3-round review-loop cap are meant to land as a cross-cutting rule inside a project's own change-type-routing table, not as a separate document to maintain.

**Where this stands today** — the review-depth exception list covers authN/authZ, payments, data migrations, secrets/infra config, unpinned new dependencies, and (self-referentially) changes to a project's own skill files or `CLAUDE.md`; a break-glass path exists for production incidents but can never skip the exception-list review or the human merge gate, only the isolation and optional-test-review steps. `skills/team-review-pipeline/pressure-scenarios.md` has 6 scenarios — the first 3 (deadline pressure on an exception-list change, a stuck review loop, AI approval mistaken for a merge) have each been run once against a fresh subagent and passed; the 3 added for the test-first, verification-evidence, and incident-pressure rules above are written but not yet run.

## How to use this in a new project

1. Copy `skills/change-type-routing/SKILL.md` (and `pressure-scenarios.md`) into the new project's `.claude/skills/change-type-routing/` (Claude Code only recognizes skills at the project level or in the user-level `~/.claude/skills/` — sitting in this repo alone won't get auto-loaded by any session).
2. Invoke the skill in that project, follow its inventory steps to produce that project's own routing table, usually written directly into that project's `CLAUDE.md`, or as a separate project-specific routing skill (see `examples/spelldungeon.md` for a worked example from the SpellDungeon project).
3. If the project already has specialized agents (`.claude/agents/*.md`), confirm their content still matches the current repo structure first — don't carry stale file paths or retired designs into the new routing table as-is.

## This repo's own conventions

This repo dogfoods its own method: `CLAUDE.md` at the root is this repo's *own* change-type-routing table (skill content, pressure-scenario files, worked examples, top-level docs) plus the cross-cutting rule that changes to any `SKILL.md` or `CLAUDE.md` get the highest scrutiny here, since these files become other projects' governance rules once copied out.

## How this repo itself stays fresh

`~/.claude/settings.json` has a global `SessionStart` hook that `git pull`s this repo (local path `~/projects/ai-workflow`) before every Claude Code session starts. A failure (offline, no remote configured yet) just prints a warning and doesn't block session start — this is a nice-to-have freshness mechanism, not a critical path.

Skill files copied into a project **do not** stay synced with this repo automatically — that's a project's own applied, concrete version, which is expected to diverge from the generic skeleton; updating it later means manually diffing and re-copying.
