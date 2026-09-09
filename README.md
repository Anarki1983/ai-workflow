# ai-workflow

*[Traditional Chinese translation available: `README.zh-TW.md`]*

This team's shared execution-stage engineering discipline for Claude Code + superpowers — synced automatically into every collaborator's global Claude Code config, not just a skeleton you copy into individual projects.

## What superpowers does not cover

superpowers already governs most of the execution stage. This repo exists only for the gap between what it does for a lone session and what a *team* needs:

| What a team needs | superpowers | This repo |
|---|---|---|
| Reviewer independence — a review by the same model that wrote the code is not a review | Absent. "Independent" upstream only ever means *task* independence. `requesting-code-review` dispatches a subagent and calls the result a code review without ever naming the reviewing model | The independence ladder, and the rule that the level reached is verified from the run record rather than assumed from the request |
| Everyone having the same rules, and the same plugin versions | Absent. superpowers is installed per person, per machine | `scripts/sync.sh` and `scripts/install.sh`: a `SessionStart` hook that pulls this repo and links its skills into every collaborator's global config |
| Some changes needing a stricter review than others | Absent. Every change is treated alike | The exception list: auth, money, migrations, secrets, governance files, unpinned dependencies |
| Who is allowed to let a change in | Half present. `finishing-a-development-branch` says the integration decision is the human's, but offers a local-merge option the AI executes and never says AI approval is insufficient | A human executes every merge, and the merge requires cloud review to have passed |
| When to stop arguing with a reviewer | Absent | A 3-round cap, and escalation defined as a scope decision rather than a correctness one |

Everything else superpowers covers — TDD, verification-before-completion, worktree isolation, plan decomposition, requesting/receiving a review — this repo defers to as-is, not reimplemented. Where this repo changes an upstream skill's behavior rather than just filling a gap, the override is named explicitly, with its exact delta, in `CLAUDE.md`'s **Relationship to superpowers** section — never restated here.

**Where this stands today:** no commercial team has run this yet. It is being proven on one real project (recorded in `examples/`) before being offered more broadly.

## What problem this repo solves

The personal `~/.claude/CLAUDE.md` can hold a **decision-stage** rule — how a developer wants to handle a new requirement before touching code. That's personal and out of scope here.

What's missing is a **team-wide execution stage**: once a decision is made and someone (human or AI) is about to touch a repo, which superpowers skill applies, how deep review should go, and who's allowed to merge — the *same* across every collaborator and project.

`skills/change-type-routing/` and `skills/team-review-pipeline/` encode this. `change-type-routing` is a method — not a pre-filled table — for inventorying which mechanism handles which kind of change. `team-review-pipeline` covers a different axis: how deep review goes, and who merges, on a team where AI leads most implementation. Its review-depth exception list, multi-model-review trigger, and 3-round review-loop cap are meant to land as cross-cutting rows in a project's own `change-type-routing` table.

Review depth is measured as **reviewer independence** rather than how much a human reads: a different human, a different model, the same model fresh with no context, or the same session — strongest first. Break-glass skips isolation for a live incident and nothing else — never the local review, the exception list, or the human merge gate. See `skills/team-review-pipeline/SKILL.md` for the full model, including how a hotfix to an already-released version reaches trunk. Its `pressure-scenarios.md` has 9 scenarios, each run against a fresh subagent.

## Dev flow

```mermaid
flowchart TD
    S0["0. Isolate the work<br/>(git worktree per work stream)"] --> S1["1. Doc/architecture gate<br/>(change fits change-type-routing)"]
    S1 --> S2["2. Implement test-first<br/>(RED before GREEN, no exceptions)"]
    S2 --> S3["3. Local review<br/>(different model reads the full diff)"]
    S3 --> S4["4. Open PR + fresh verification output<br/>cloud review loop, capped at 3 rounds"]
    S4 --> S5["5. Human merges the PR<br/>(non-negotiable — AI approval alone is never enough)"]
    S5 --> S6["6. CI/CD deploys to a test environment"]
    S6 -- validation fails --> S2
    S6 -- validation passes --> Done(["Done"])
    Incident(["Live production incident"]) -. "break-glass: skips 0 only" .-> S2
```

`skills/team-review-pipeline/SKILL.md` is the source of truth for each step and the exception list; this is a picture, not a substitute for reading it.

## How the sync works

Every collaborator runs this once:

```
bash scripts/install.sh
```

That one-time step: backs up `~/.claude/settings.json`, points its `SessionStart` hook at `scripts/sync.sh`, and adds a single `@<this-repo-path>/CLAUDE.md` line to the collaborator's personal `~/.claude/CLAUDE.md` (nothing else in that file is touched). From then on, **every session start** re-runs `scripts/sync.sh`, which:

1. Pulls this repo.
2. Symlinks each `skills/*` and `agents/*` subdirectory into the collaborator's global `~/.claude/skills/` and `~/.claude/agents/` — skipping and warning about anything already at that path that isn't its own symlink, never overwriting. It also prunes the reverse: a link this repo created for a skill or agent that no longer exists here gets deleted and reported, so a rename or removal propagates instead of leaving a dangling link. There is no `agents/` directory yet — the script's `sync_dir` returns early on an absent source, so nothing is linked and nothing warns.
3. Reconciles third-party plugins against `scripts/third-party-plugins.json` (see below) — installs anything missing, reports drift from a recorded version, never force-changes an installed version.

This makes onboarded collaborators self-healing: add a skill here, everyone picks it up next session, no manual re-sync. It can't solve a brand-new collaborator's *first* install, though — nothing runs until `scripts/install.sh` has; that's a one-time, documented onboarding step, not a mechanism.

**What stays per-project:** the *output* of `change-type-routing` — a specific project's actual routing table — belongs in that project's own `CLAUDE.md`. Only the method for producing it is global.

**Trust model, stated plainly:** `scripts/sync.sh` and `scripts/install.sh` run unattended on every collaborator's machine, self-updating via `git pull`. Whoever merges a change to `scripts/` runs arbitrary code on every machine at next session start — which is why `CLAUDE.md` holds `scripts/*` to a higher scrutiny tier than skill content.

## Keeping third-party plugins consistent

`scripts/third-party-plugins.json` lists the third-party plugins (superpowers, mattpocock-skills, etc.) this team expects on every machine. `scripts/sync.sh` checks every session: missing → auto-installs; installed at a different version than recorded → warns either direction, never forces a change.

**Version tracking here is advisory, not a real pin.** `claude plugin install` has no flag to request a specific version, so a missing plugin installs at whatever the marketplace currently serves — the recorded version is something to report against, not enforce. It's also semver-only: a plugin the marketplace versions by its own commit sha (which changes on every upstream commit) is left untracked on purpose, since comparing it would warn every session forever.

Adding a plugin or bumping a recorded version is a deliberate, reviewed edit — see `CLAUDE.md`'s table for the bar.

## For projects or people outside this team

If you're not on this team's synced setup — evaluating this repo standalone, or adapting it for a different team — the underlying skills still work copied manually: copy `skills/change-type-routing/SKILL.md` (and its `pressure-scenarios.md`) into a project's `.claude/skills/change-type-routing/`, invoke it there, and follow its inventory steps to produce that project's own routing table (see `examples/spelldungeon.md` for a worked example). Files copied this way don't stay synced with this repo automatically; that's expected to diverge into a project's own concrete version.

## This repo's own conventions

`CONTEXT.md` at the root is this repo's glossary — the terms its rules are written in (`Author`, `Reviewer independence`, `Merge gate`, `Local review`, `Cloud review`). It is a glossary and nothing else: no rules, no rationale, no implementation detail.

This repo dogfoods its own method: `CLAUDE.md` at the root is this repo's *own* change-type-routing table — one row per change type (skill content, agent definitions, pressure-scenario files, worked examples, design specs and plans, sync/install scripts, plugin pin, glossary, top-level docs), each stating what a PR in that category must attach, plus cross-cutting rules covering how review works here and who merges.

**That table is deliberately not reproduced here** — an English reader can just read the short `CLAUDE.md`. `README.zh-TW.md` does keep a translation of it, the one duplication in this repo that's on purpose; `scripts/check_repo.py` compares the two tables' change-type lists and fails CI on drift, so the duplication stays honest.

Two things from it matter to a reader evaluating this repo:

- **Mechanical checks run in CI** on every PR and push to `main`: `shellcheck`, a Python/JSON syntax check, and `scripts/check_repo.py`, which catches what goes stale silently in a prose repo — a skill missing from the README, a frontmatter `description` that drifts into summarising the workflow, a skill with no `pressure-scenarios.md`. Safe to run by hand any time. There's no branch protection, so CI reports rather than blocks.
- **Two categories must attach evidence to the PR:** a skill-file change attaches its `pressure-scenarios.md` run; a change to a script that runs on collaborators' machines attaches a throwaway-environment run. Neither ranks above the other — they fail in different units.

**PR granularity:** one skill, one agent, or one fix per PR, so this repo's pieces stay independently diffable, syncable, and revertible.

**Language:** skill, agent, and doc content (including script comments) is English; `README.zh-TW.md` is the one deliberate translation exception.
