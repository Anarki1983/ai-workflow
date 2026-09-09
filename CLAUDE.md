# ai-workflow — project conventions

This repo is this team's shared execution-stage engineering discipline (see `README.md`) — its `skills/` and `agents/` are symlinked into every collaborator's global `~/.claude/skills/` and `~/.claude/agents/` by `scripts/sync.sh`, run on every session via a `SessionStart` hook. It is now the actual source of what every collaborator's Claude Code session can do, not just a skeleton to copy elsewhere — which raises the bar on review here, not lowers it.

Most of this repo is prose (skill files, worked examples); `scripts/*.sh` and `scripts/*.py` are executable code that runs, unattended, on every collaborator's machine on every session start. Neither is ranked above the other — they fail in different units, so the question is never which is more serious but what each needs in order to be trusted. Every row below answers that question for its own category.

This file governs execution-stage conventions for changes *inside this repo*. Decision-stage routing (should a change be discussed first, or go straight to plan mode) is owned by the personal `~/.claude/CLAUDE.md`, not by this file.

## Change types in this repo

| Change type | Files | What's required |
|---|---|---|
| Skill content | `skills/*/SKILL.md` | Frontmatter `description` stays in the "Use when..." trigger-only form (superpowers:writing-skills SDO rule — never summarize the skill's workflow in the description). Any content change must be re-validated against that skill's own `pressure-scenarios.md` before merge — run the relevant scenarios (or add a new one covering the change) and keep the transcript evidence, per superpowers:verification-before-completion (no completion claim without evidence). A run showing the scenario passing *with* the skill is half the evidence; superpowers:writing-skills requires the baseline failure without it. Do not restate its rule here — defer to it. |
| Agent definitions | `agents/*` | Same bar as skill content: read fully before merge, since these become every collaborator's callable subagent types once synced. |
| Pressure-scenario files | `skills/*/pressure-scenarios.md` | Adding or editing a scenario requires at least one actual subagent run showing pass/fail evidence attached to the PR — a written-but-never-run scenario is not validated, it's a draft. |
| Worked examples | `examples/*.md` | Must reflect a real applied case. If no real project has applied the method yet, say so explicitly in the file rather than presenting a plausible-looking fabrication as a worked example. |
| Design specs and plans | `docs/superpowers/specs/*`, `docs/superpowers/plans/*` | A record of a decision and its argument, not a rule anyone follows automatically — so no pressure-scenario run is required. It must name the spec it implements (plans) or the discussion it settles (specs), and once its work has merged it is not edited to match what was actually built; a superseding document is written instead. |
| Scripts that run on a collaborator's machine | `scripts/sync.sh`, `scripts/install.sh`, `scripts/sync_plugins.py` | The changed script must be run in a throwaway environment (a fake `CLAUDE_CONFIG_DIR`, a fake `HOME`, a scratch repo — whatever isolates it), with the command and its output attached to the PR. Never on a real machine to "check it works". Reading the code tells you what it looks like it does; running it tells you which files it actually touched. |
| Third-party plugin pin | `scripts/third-party-plugins.json` | A version bump is a deliberate, reviewed decision (what changed upstream, why it's safe to move to), not a routine dependency-bot update — see `skills/team-review-pipeline/SKILL.md`'s unpinned-dependency row for why this category exists at all. |
| Glossary | `CONTEXT.md` | Changing or removing a term means every document that uses it changes in the same PR — a term with two live meanings is worse than no glossary at all. Definitions only: no rules, no rationale, no implementation detail. |
| Top-level docs | `README.md`, `README.zh-TW.md` | Update whenever a skill, agent, or script is added, renamed, or removed — check the skill list and cross-references stay accurate. `README.zh-TW.md` may lag `README.md` briefly but should not drift permanently; `README.md` is authoritative on conflict. |

## Cross-cutting rules (priority over every row above)

**1. Every change is read by a judgment that did not produce it.** Terms below are defined in `CONTEXT.md`. Before a PR exists, the diff gets a **local review**: a model other than the one that wrote it, running as a subagent. That is where reviewer independence is actually secured, because it is the only review that happens while the change is still cheap to redirect. On the PR, **cloud review** runs as a second net. A merge requires cloud review to have passed — a merge gate that consumes no information is a rubber stamp, and the cloud review verdict is what the human's merge decision is made of.

**2. A human executes the merge, and decides scope rather than correctness.** This is not a local concession to how small this repo is — it is how the workflow in `skills/team-review-pipeline/` works in every project it governs: **a human does not read a diff unless there is a specific reason to.** Reading is what the two reviews above are for, and a human reading in the normal course of work means one of them is not being trusted to do its job. What the human decides is whether this change belongs in the repo at all, and whether it belongs now. If cloud review and local fixes have not converged after three rounds, stop looping: the human kills the branch, re-scopes the change, or overrides the review — and an override is written down with its reason, since it is the one place in this pipeline where a person's judgment outranks a machine's.

**3. Neither evidence requirement above is optional, and neither substitutes for the other.** The two categories that carry one carry it for unrelated reasons, and both reasons survive independently of how serious the other sounds:

- **Governance files** (`skills/*/SKILL.md`, this file, `CONTEXT.md`) become other projects' or every collaborator's rules once synced or copied out. A wording bug — an ambiguous instruction, a dropped exception, a description that leaks the workflow — propagates silently, and no test suite anywhere catches it. The pressure-scenario run is what stands in for that missing test suite.
- **Scripts that run on a collaborator's machine** *execute*, unattended, with the local permissions of every collaborator who has the sync hook installed, every time they start a session. Whoever merges here runs code on every collaborator's machine. That is accepted in exchange for the scripts self-updating via `git pull` rather than everyone re-running `scripts/install.sh` for each logic change — but the trade only holds if the isolated run in that row actually happens, every time. A script under `scripts/` that only ever runs in CI is not in this category: CI running it *is* the isolated run.

## Relationship to superpowers

superpowers is a dependency, pinned in `scripts/third-party-plugins.json`, not
something this repo reimplements. Everything it covers, it owns. This repo
carries only what superpowers lacks, plus the overrides below — each of which
names the upstream skill it changes and states exactly what the delta is.

An override is not a fork: the upstream skill's mechanics still apply, and
upstream fixes still reach us. Only the named delta differs.

| superpowers skill | Disposition |
|---|---|
| `requesting-code-review` | **Override.** Its mechanics stand — SHA range, reviewer template, context crafted for the reviewer rather than the session's history. Its default reviewer does not: absent a configured default reviewing model it dispatches the authoring model in a fresh session, which is level 3. The reviewer's model is chosen deliberately and read back from the run record, per `skills/team-review-pipeline/SKILL.md` step 3. |
| `finishing-a-development-branch` | **Override.** Drop the *merge back to base locally* option wherever it appears; the remaining options stand unchanged. Integration always goes through a pull request, and a human executes the merge. Once the PR is merged, the skill's own Step 6 cleanup (worktree removal, branch deletion) still applies, per `skills/team-review-pipeline/SKILL.md`. |
| `writing-skills` | **Defer to it.** Its Iron Law — no skill edit without first watching an agent fail *without* the skill — is stricter than what this file's own rows state, so those rows defer to it rather than restating a weaker parallel version. When the two ever appear to disagree, superpowers:writing-skills wins. |

Every other superpowers skill is adopted as-is and is never restated here.
`subagent-driven-development` was checked specifically for a conflict with the
merge gate and has none: it already names "a merge, a push to a shared branch"
among the four things that stop a running plan.

## PR granularity

One skill, one agent, or one fix per PR. Don't bundle unrelated changes — this repo's whole purpose is to be diffed and its pieces synced or copied independently, so a PR that mixes two unrelated things makes that harder to review and harder to revert later.

## Language

Skill, agent, and doc content in this repo is written in English (see `skills/*/SKILL.md`, `README.md`, `examples/*.md` for the current baseline); `README.zh-TW.md` is the one deliberate exception, kept as a translation. Script comments are also English. This is independent of whatever language a session uses to talk about the repo.
