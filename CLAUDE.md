# ai-workflow — project conventions

This repo is this team's shared execution-stage engineering discipline (see `README.md`) — its `skills/` and `agents/` are symlinked into every collaborator's global `~/.claude/skills/` and `~/.claude/agents/` by `scripts/sync.sh`, run on every session via a `SessionStart` hook. It is now the actual source of what every collaborator's Claude Code session can do, not just a skeleton to copy elsewhere — which raises the bar on review here, not lowers it.

Most of this repo is still prose (skill files, worked examples) with no tests-only shortcut — every prose change gets a full human read of the diff. `scripts/*.sh` and `scripts/*.py` are the one real exception: they are executable code that runs, unattended, on every collaborator's machine on every session start. See the cross-cutting rule below — this category is scrutinized *harder* than prose, not folded into the same tests-only-doesn't-apply default.

This file governs execution-stage conventions for changes *inside this repo*. Decision-stage routing (should a change be discussed first, or go straight to plan mode) is owned by the personal `~/.claude/CLAUDE.md`, not by this file.

## Change types in this repo

| Change type | Files | What's required |
|---|---|---|
| Skill content | `skills/*/SKILL.md` | Frontmatter `description` stays in the "Use when..." trigger-only form (superpowers:writing-skills SDO rule — never summarize the skill's workflow in the description). Any content change must be re-validated against that skill's own `pressure-scenarios.md` before merge — run the relevant scenarios (or add a new one covering the change) and keep the transcript evidence, per superpowers:verification-before-completion (no completion claim without evidence). |
| Agent definitions | `agents/*` | Same bar as skill content: read fully before merge, since these become every collaborator's callable subagent types once synced. |
| Pressure-scenario files | `skills/*/pressure-scenarios.md` | Adding or editing a scenario requires at least one actual subagent run showing pass/fail evidence attached to the PR — a written-but-never-run scenario is not validated, it's a draft. |
| Worked examples | `examples/*.md` | Must reflect a real applied case. If no real project has applied the method yet, say so explicitly in the file rather than presenting a plausible-looking fabrication as a worked example. |
| Sync/install scripts | `scripts/*.sh`, `scripts/*.py` | See the cross-cutting rule below — this is the repo's highest-scrutiny category, above even skill content. |
| Third-party plugin pin | `scripts/third-party-plugins.json` | A version bump is a deliberate, reviewed decision (what changed upstream, why it's safe to move to), not a routine dependency-bot update — see `skills/team-review-pipeline/SKILL.md`'s unpinned-dependency row for why this category exists at all. |
| Top-level docs | `README.md`, `README.zh-TW.md` | Update whenever a skill, agent, or script is added, renamed, or removed — check the skill list and cross-references stay accurate. `README.zh-TW.md` may lag `README.md` briefly but should not drift permanently; `README.md` is authoritative on conflict. |

## Cross-cutting rules (priority over every row above)

**1. Any change touching a `SKILL.md` or this `CLAUDE.md` file is a highest-scrutiny category.** These files become other projects' or every collaborator's governance rules once synced or copied out — a subtle wording bug here (an ambiguous instruction, a dropped exception, a description that leaks the workflow) propagates silently, with no test suite anywhere to catch it. Never skip a full read of the diff because "it's just wording" or "just a small addition."

**2. Any change to `scripts/*.sh` or `scripts/*.py` is scrutinized above that.** A bug or a hostile edit in a SKILL.md misleads an AI reading text; a bug or a hostile edit in these scripts *executes*, unattended, with the local permissions of every collaborator who has this repo's sync hook installed, every time they start a session. Whoever can merge a change here can run arbitrary code on every collaborator's machine. This is accepted in exchange for the scripts self-updating via `git pull` (see `skills/team-review-pipeline/SKILL.md`'s dev-flow step 0 discussion) rather than requiring everyone to manually re-run `scripts/install.sh` for every logic change — but the trade only holds if this category actually gets read line-by-line before merge, every time, by someone other than the author.

## PR granularity

One skill, one agent, or one fix per PR. Don't bundle unrelated changes — this repo's whole purpose is to be diffed and its pieces synced or copied independently, so a PR that mixes two unrelated things makes that harder to review and harder to revert later.

## Language

Skill, agent, and doc content in this repo is written in English (see `skills/*/SKILL.md`, `README.md`, `examples/*.md` for the current baseline); `README.zh-TW.md` is the one deliberate exception, kept as a translation. Script comments are also English. This is independent of whatever language a session uses to talk about the repo.
