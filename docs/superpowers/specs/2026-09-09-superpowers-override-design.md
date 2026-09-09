# Design: state this repo as an override of superpowers, not a parallel workflow

**Date:** 2026-09-09
**Status:** approved design, not yet implemented

## Context

This repo is a proof of concept for introducing an AI-led workflow into
commercial software development with an existing team. It is currently written
in the voice of a team that already uses it, and its two skills restate a
substantial amount of what `superpowers` already says.

An audit against the installed superpowers 6.3.0 produced the finding this
design responds to: of everything in this repo, only a small part closes a gap
superpowers actually has.

| This repo's content | superpowers | Verdict |
|---|---|---|
| Reviewer independence (a same-model review is not a review) | Absent. "Independent" in superpowers only ever means *task* independence. `requesting-code-review` dispatches a `general-purpose` subagent and calls the result a code review, never mentioning the reviewing model | Real gap — and the one place superpowers is not merely silent but actively misleading |
| Distribution and version consistency (`scripts/sync.sh`, `install.sh`, the plugin manifest) | Absent. superpowers is installed per machine, per person | Real gap, and this repo's only executable mechanism rather than prose |
| Risk tiering (the exception list) | Absent. Every change is treated alike | Real gap |
| Merge authority | Half present. `finishing-a-development-branch` says "the integration decision is theirs", but offers a local-merge option the AI executes, and never says AI approval is insufficient | Partial gap: same direction, weaker |
| Review-loop cap and what escalation means | Absent | Real gap, small |
| Release branching and hotfix direction | Absent | Real gap, but generic trunk-based knowledge rather than anything AI-specific |
| Change-type routing | No equivalent, though superpowers' model is "each skill declares its own trigger". The difference only bites for *non-superpowers* mechanisms: check scripts, `npm run` targets, a project's own methodology | Narrow gap |
| Three-layer CLAUDE.md split | This is a Claude Code feature, not an invention of this repo | Not a gap |
| TDD, verification, worktrees, plans | Restated verbatim | None |

The conclusion this design implements: **the repo should exist, at roughly a
third of its current size, and should state its relationship to superpowers
explicitly instead of quietly paralleling it.**

## Decision: explicit override, not vendoring

The rejected alternative was vendoring superpowers' skills into `skills/` and
editing them freely. Two reasons it was rejected:

- Upstream divergence becomes permanent. superpowers is actively developed;
  every upstream fix would become a manual reconciliation.
- `scripts/sync.sh` symlinks `skills/*` into `~/.claude/skills/`, so a vendored
  `test-driven-development` would coexist with the plugin's
  `superpowers:test-driven-development`. Which one an agent loads has not been
  verified, and ambiguity about which discipline is in force is worse than a
  missing rule. The repo would also both depend on superpowers (via
  `scripts/third-party-plugins.json`) and replace it.

Instead, superpowers stays a dependency, and this repo carries only two kinds
of content: **what superpowers lacks**, and **explicit overrides of named
superpowers skills**, each stating its delta.

## 1. The override table

Lives in this repo's `CLAUDE.md`, which `scripts/install.sh` already imports
into each collaborator's personal `~/.claude/CLAUDE.md`, so it loads every
session. It is must-see and thin, which is what that file is for. No new
mechanism is needed.

| superpowers skill | Disposition |
|---|---|
| `requesting-code-review` | **Override.** Its mechanics stand — SHA range, reviewer template, context crafted for the reviewer. Its default reviewer does not: absent a configured default reviewing model it runs the authoring model in a fresh session, which is level 3. The reviewer's model must be chosen and read back from the run record, per `team-review-pipeline` step 3 |
| `finishing-a-development-branch` | **Override.** Drop option 1 (merge back to base locally) from its menu. Integration always goes through a PR, and a human executes the merge |
| `writing-skills` | **Defer to it.** Its Iron Law — no skill edit without first watching an agent fail without the skill — is stricter than this repo's current evidence rule. Adopt it; delete the weaker local restatement rather than maintaining a softer parallel rule |
| The remaining eleven | **Adopt as-is.** This repo does not restate them |

`subagent-driven-development` was checked for a conflict with the merge gate
and has none: it already names "a merge, a push to a shared branch" among the
four things that stop a running plan.

**CI guard:** `scripts/check_repo.py` gains a check that every skill named in
the table exists in the installed superpowers. An upstream rename or removal
then fails CI instead of leaving the table pointing at nothing.

## 2. `skills/team-review-pipeline/SKILL.md` shrinks

Currently 3047 words. Target 1200–1400. Nothing is deleted as a *rule*;
everything cut is a restatement of a skill that says it better, replaced by a
reference.

**Kept in full** (all original, none of it in superpowers): who reads a diff
and the two specific reasons; the independence ladder; "the level reached is
verified, not requested"; the two review layers; the exception list; step 3's
local review and its override; step 4's cloud review, 3-round cap and
escalation semantics; step 5's human merge gate; the break-glass path.

**Cut to a single reference line:** the "tests are still written first"
argument (it is `test-driven-development`'s own argument); step 0's worktree
rationale; step 2's TDD and verification rationale; "breaking large changes
into reviewable pieces".

**Cut to roughly 60 words:** the three-layer CLAUDE.md split, keeping only the
actionable part — the concrete rows a project's routing table must carry (the
independence level it actually reaches, the loop cap number, its branching
model, and any category where it has declared that a human does read the diff).

### The release model changes

The current section (~700 words) maintains long-lived `release/x.y` branches
and forks on whether the project controls its own release timing. It is
replaced by one mechanism, in under 100 words:

1. A release is a tag on trunk.
2. A hotfix branches from that tag.
3. The fix is made there and tagged again, which is what drives CI/CD.
4. That branch is merged back into trunk.

This covers both the self-timed and the externally-gated case with one
mechanism instead of a decision fork, and no branch outlives its incident.

Its one weakness is that step 4 is a deferred obligation, at exactly the moment
— the incident is over, production is healthy — when it is most likely to be
skipped, which loses the fix at the next release. The rule closes this without
adding an obligation, by identifying step 4 with one the break-glass path
already requires:

> The PR that merges the hotfix branch back into trunk **is** the postmortem PR
> that break-glass requires, within the same window. Until it lands, the fix
> does not exist on trunk, and any release cut from trunk in the meantime ships
> the original bug.

Operational note, deliberately not written into the skill because it varies by
forge: the CI/CD trigger must accept a tag that is not on trunk, or the hotfix
tag will deploy nothing. Verify this on day one of a real import.

## 3. The rest of the repo

- **`README.md`** — rewritten, not trimmed. Its "Team review pipeline at a
  glance" section reproduces SKILL.md's step table, ladder, exception list and
  diagrams, and admits in its own text that SKILL.md is the source of truth if
  the copy drifts. Cut it; keep one dev-flow diagram. In its place goes the
  argument that is currently missing entirely: **what superpowers does not
  cover**, which is what a colleague evaluating this actually needs. It serves
  both audiences — the argument first, then installation and operation.
  `examples/spelldungeon.md` stays in the repo as an internal record but is
  **not** cited as evidence in the README. This leaves the argument resting on
  its own reasoning rather than on a worked case; that is accepted.
- **`README.zh-TW.md`** — follows. English stays authoritative, per the
  existing convention.
- **`CLAUDE.md`** — gains the override table. Its change-type table and three
  cross-cutting rules are unchanged; they are original and in use.
- **`CONTEXT.md`** — unchanged.
- **`agents/`** — deleted. An empty directory whose README explains its own
  emptiness. Recreate it when a real agent exists. `scripts/sync.sh` must
  tolerate its absence.
- **`scripts/*`** — kept. `check_repo.py` gains the override-table check.
- **`skills/change-type-routing/`** — kept. superpowers has no equivalent. Its
  `pressure-scenarios.md` has never been run, which is outstanding work rather
  than a design question.

## Non-goals

- Onboarding a second collaborator. That is what the POC is for, and it comes
  after this.
- Configuring branch protection or any forge-side enforcement of the merge
  gate. Still out of scope, still worth noticing when it is unconfigured.
- Proving the merge gate, level 1 review, or sync collision handling. These are
  structurally unprovable with one person and one machine, and must not be part
  of any exit criterion for the POC.

## Decomposition

This repo's own rule is one skill, one agent, or one fix per PR, so this lands
as separate PRs rather than one:

1. The override table in `CLAUDE.md`, plus its `check_repo.py` guard.
2. `team-review-pipeline` shrink, including the new release model.
3. `README.md` and `README.zh-TW.md` rewrite.
4. `agents/` removal, with the `sync.sh` change that tolerates it.

**In-flight coordination:** the open PR on `docs/compose-review-subskills`
edits the same step 3 that item 2 rewrites. Merge it first — its content is
precisely what the override table formalizes, so it is not wasted work, and
rebasing item 2 on top is cheaper than reconciling two rewrites of one section.

## Verification

Per this repo's own `CLAUDE.md`, each PR above carries what its change type
requires: skill-content changes are re-validated against the relevant
`pressure-scenarios.md` with the run transcript attached, a level-2 local
review reads the diff before the PR exists, and `scripts/check_repo.py` and CI
pass. The `sync.sh` change in item 4 runs in a throwaway environment with its
output attached, never on a real machine.

Item 2 additionally needs a scenario covering the new release model: a live
incident on a shipped version, where the agent must branch from the tag, and
must treat the merge back to trunk as the postmortem PR rather than as
something to do later.
