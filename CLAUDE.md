# ai-workflow — project conventions

This repo is a skeleton of meta-skills for execution-stage engineering discipline (see `README.md`). It has no application code and no test suite — its only artifacts are skill files, worked examples, and this document. That changes what "review" means here: there is no tests-only shortcut, because there's nothing compiled or test-verified to lean on. Every change gets a full human read of the actual prose diff.

This file governs execution-stage conventions for changes *inside this repo*. Decision-stage routing (should a change be discussed first, or go straight to plan mode) is owned by the personal `~/.claude/CLAUDE.md`, not by this file.

## Change types in this repo

| Change type | Files | What's required |
|---|---|---|
| Skill content | `skills/*/SKILL.md` | Frontmatter `description` stays in the "Use when..." trigger-only form (superpowers:writing-skills SDO rule — never summarize the skill's workflow in the description). Any content change must be re-validated against that skill's own `pressure-scenarios.md` before merge — run the relevant scenarios (or add a new one covering the change) and keep the transcript evidence, per superpowers:verification-before-completion (no completion claim without evidence). |
| Pressure-scenario files | `skills/*/pressure-scenarios.md` | Adding or editing a scenario requires at least one actual subagent run showing pass/fail evidence attached to the PR — a written-but-never-run scenario is not validated, it's a draft. |
| Worked examples | `examples/*.md` | Must reflect a real applied case. If no real project has applied the method yet, say so explicitly in the file rather than presenting a plausible-looking fabrication as a worked example. |
| Top-level docs | `README.md` | Update whenever a skill is added, renamed, or removed — check the skill list and cross-references stay accurate. |

## Cross-cutting rule (priority over every row above)

**Any change touching a `SKILL.md` or this `CLAUDE.md` file is this repo's highest-scrutiny category.** These files become other projects' governance rules once copied out — a subtle wording bug here (an ambiguous instruction, a dropped exception, a description that leaks the workflow) propagates silently into every project that copies it, with no test suite anywhere to catch it. Never skip a full read of the diff because "it's just wording" or "just a small addition" — that rationalization is exactly what superpowers:writing-skills' Iron Law exists to block for skill files, and it applies with equal force to this file.

## PR granularity

One skill (or one fix within one skill) per PR. Don't bundle unrelated skill changes — this repo's whole purpose is to be diffed and copied piecemeal into other projects, so a PR that mixes two unrelated skills makes that harder to review and harder to cherry-pick later.

## Language

Skill and doc content in this repo is written in English (see `skills/*/SKILL.md`, `README.md`, `examples/*.md` for the current baseline). This is independent of whatever language a session uses to talk about the repo.

## If this repo ever gains real code

It currently has none — no lint config, no build, no CI. If that changes (e.g., a script that validates SKILL.md frontmatter), add it as its own row in the table above and pull in `superpowers:test-driven-development` for it; don't retrofit the tests-only review model from `skills/team-review-pipeline/` onto this repo without first confirming it actually has a test suite for AI-authored code to lean on — that skill's default assumes one exists, and here it currently doesn't.
