# ai-workflow

*[Traditional Chinese translation available: `README.zh-TW.md`]*

This team's shared execution-stage engineering discipline for Claude Code + superpowers — synced automatically into every collaborator's global Claude Code config, not just a skeleton you copy into individual projects.

## What problem this repo solves

The personal `~/.claude/CLAUDE.md` (per-developer, per-machine) can hold a **decision-stage** rule — how a given developer wants to handle a new requirement, new feature, or behavior change before touching code. What that rule actually says, and which skills or process it leans on, varies per person; this repo has no business assuming every collaborator has the same ones installed. That rule solves "should we do this, and how" — but it's personal, not something a team can share as-is without overwriting everyone's individual preferences.

What's missing is a **team-wide execution stage**: once a decision is made and someone (human or AI) is actually about to touch a repo, which superpowers skill a given change should use (TDD? systematic-debugging? frontend-design?), which specialized agent to call, how deep review should go, and who's allowed to merge — this needs to be the *same* across every collaborator and every project they touch, or the whole point of having a shared standard is lost.

`skills/change-type-routing/` and `skills/team-review-pipeline/` are the two skills that encode this. `skills/change-type-routing/` is a method — not a pre-filled table — for helping a project inventory which mechanism (skill/agent/check) handles which kind of change. `skills/team-review-pipeline/` covers a different axis of the same execution stage: not *which* mechanism handles a change, but *how deep review goes* and *who is allowed to merge* on a team where AI leads most implementation. It composes existing superpowers skills rather than inventing new ones: superpowers:test-driven-development and superpowers:verification-before-completion gate what "tests pass" is allowed to mean; superpowers:using-git-worktrees isolates concurrent work; superpowers:writing-plans / executing-plans break large changes into one-PR-per-task; superpowers:finishing-a-development-branch handles cleanup after merge. Its review-depth exception list, multi-model-review trigger, and 3-round review-loop cap are meant to land as a cross-cutting rule inside a project's own change-type-routing table.

**Where this stands today** — the review-depth exception list covers authN/authZ, payments, data migrations, secrets/infra config, unpinned new dependencies, and (self-referentially) changes to a project's own skill files or `CLAUDE.md`; a break-glass path exists for production incidents but can never skip the exception-list review or the human merge gate, only the isolation and optional-test-review steps. `skills/team-review-pipeline/pressure-scenarios.md` has 6 scenarios — the first 3 (deadline pressure on an exception-list change, a stuck review loop, AI approval mistaken for a merge) have each been run once against a fresh subagent and passed; the 3 added for the test-first, verification-evidence, and incident-pressure rules are written but not yet run.

## How the sync works

Every collaborator runs this once:

```
bash scripts/install.sh
```

That one-time step: backs up `~/.claude/settings.json`, points its `SessionStart` hook at `scripts/sync.sh`, and adds a single `@<this-repo-path>/CLAUDE.md` line to the collaborator's personal `~/.claude/CLAUDE.md` (nothing else in that file is touched). From then on, **every session start** re-runs `scripts/sync.sh`, which:

1. Pulls this repo.
2. Symlinks each `skills/*` and `agents/*` subdirectory into the collaborator's global `~/.claude/skills/` and `~/.claude/agents/` — skipping (and warning about, never overwriting) anything already at that path that isn't already this repo's own symlink.
3. Reconciles third-party plugins against `scripts/third-party-plugins.json` (see below) — installs anything missing, warns on version drift, never force-changes an installed version.

This makes already-onboarded collaborators self-healing: add a skill to this repo, and everyone picks it up on their next session, no manual re-sync. The one thing this can't solve is a brand-new collaborator's very first install — nothing enforces that `scripts/install.sh` gets run, since nothing runs until it has; that's a one-time onboarding step, documented, not a mechanism.

**What stays per-project, not global:** the *output* of `change-type-routing` — the actual routing table for a specific project's directory structure — still belongs in that project's own `CLAUDE.md`, since that content is inherently project-specific. Only the skill (the method for producing that table) is global.

**Trust model, stated plainly:** `scripts/sync.sh` and `scripts/install.sh` are executable code that runs unattended on every collaborator's machine, self-updating via `git pull`. Whoever can merge a change to `scripts/` can run arbitrary code on every collaborator's machine on their next session. This repo's own `CLAUDE.md` puts changes to `scripts/*` at a higher scrutiny tier than skill content for exactly this reason — see its cross-cutting rules.

## Keeping third-party plugins consistent

`scripts/third-party-plugins.json` pins the exact version of each team-authored-elsewhere plugin (superpowers, mattpocock-skills, etc.) this team has agreed on. `scripts/sync.sh` checks every session: missing entirely → auto-installs; installed but the wrong version → warns (in both directions, behind or ahead of the pin) rather than forcing a change, since the `claude plugin` CLI has no exact-version-install/downgrade command to force it. Bumping the pinned version is a deliberate, reviewed edit to that file, not a routine update — see `CLAUDE.md`'s table for the review bar on it.

## For projects or people outside this team

If you're not on this team's synced setup — evaluating this repo standalone, or adapting it for a different team — the underlying skills still work copied manually: copy `skills/change-type-routing/SKILL.md` (and its `pressure-scenarios.md`) into a project's `.claude/skills/change-type-routing/`, invoke it there, and follow its inventory steps to produce that project's own routing table (see `examples/spelldungeon.md` for a worked example). Files copied this way don't stay synced with this repo automatically; that's expected to diverge into a project's own concrete version.

## This repo's own conventions

This repo dogfoods its own method: `CLAUDE.md` at the root is this repo's *own* change-type-routing table (skill content, agent definitions, pressure-scenario files, worked examples, sync/install scripts, top-level docs), plus cross-cutting rules that put governance-file and sync-script changes at the highest scrutiny here — the latter above the former, since scripts execute unattended while prose only gets read.
