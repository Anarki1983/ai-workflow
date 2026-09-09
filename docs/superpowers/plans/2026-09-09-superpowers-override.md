# Superpowers Override Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restate this repo as an explicit override of superpowers rather than a parallel workflow, cutting everything that merely repeats an upstream skill.

**Architecture:** superpowers stays a dependency, pinned in `scripts/third-party-plugins.json`. This repo carries only two kinds of content: what superpowers lacks, and named overrides of specific superpowers skills. The override table lives in `CLAUDE.md`, which `scripts/install.sh` already imports into each collaborator's personal `~/.claude/CLAUDE.md`, so it loads every session with no new mechanism. `scripts/check_repo.py` guards the table against upstream renames.

**Tech Stack:** Markdown prose; Python 3 for `scripts/check_repo.py`; bash for `scripts/sync.sh`; GitHub Actions for CI.

**Spec:** `docs/superpowers/specs/2026-09-09-superpowers-override-design.md`

## Global Constraints

- Skill, agent, and doc content is written in **English**, including script comments. `README.zh-TW.md` is the single deliberate translation; `README.md` is authoritative on conflict.
- Every `skills/*/SKILL.md` frontmatter `description` stays in the trigger-only "Use when..." form. Never summarise the skill's workflow there (superpowers:writing-skills SDO rule). `scripts/check_repo.py` enforces this.
- **All three tasks land in one PR, on one branch, as three commits.** This is a deliberate override of this repo's own one-fix-per-PR rule, requested by the project owner to avoid the cost of resolving conflicts between three PRs that edit overlapping prose. Per this repo's own escalation rule an override is recorded with its reason, so the PR body states it. Each task still ends with its own level-2 local review — what is being collapsed is branching and merging, not review.
- A **level-2 local review** (a model other than the authoring one, confirmed from the run transcript rather than from the request) reads the full diff before each PR is opened. Every task here touches `skills/*/SKILL.md` or `CLAUDE.md`, which are governance files on the exception list, so this is mandatory, not discretionary.
- **A human executes every merge**, and a merge requires cloud review to have passed. No task below is complete when its branch is pushed; it is complete when a human has merged it.
- Skill-content changes are re-validated against that skill's `pressure-scenarios.md`, with the transcript recorded in that file's run log.
- Work happens in a git worktree per task (superpowers:using-git-worktrees), branched from `origin/main`.
- `python3 scripts/check_repo.py` must exit 0 before any PR is opened.

## Deviations from the spec, and why

- The spec listed **four** PRs; this plan has **three**. Removing `agents/` was going to be its own PR, but the only coupling that made it PR-sized — dropping the "Agent definitions" row from `CLAUDE.md`, which would force a matching edit to `README.zh-TW.md`'s translated table or fail CI — is avoided by **keeping that row**. The row is a pre-registered review bar for a file type that may appear later; it costs one line and prevents an agent being added with no rule attached. What actually goes is the empty directory and its README, which is a two-file deletion that belongs with the README rewrite in task 3.
- The spec said `scripts/sync.sh` "must tolerate" a missing `agents/`. It already does: `sync_dir` returns early at `scripts/sync.sh:25` when the source directory is absent, and `prune_dir` at `scripts/sync.sh:54` when the destination is. **No script change is needed**, so task 3 carries no script-modification evidence requirement. It does verify the runtime behaviour once, in an isolated environment, because deleting the directory changes what the script does even though its text is unchanged.
- Task order is fixed: task 1 before task 2, because task 1 puts superpowers:writing-skills' Iron Law into force and task 2's new pressure scenario is the first thing required to obey it.
- The three tasks land as **one PR** rather than three, at the project owner's request, to avoid resolving conflicts between PRs that edit overlapping prose. This overrides the repo's PR-granularity rule and is recorded in the PR body with its reason. The spec and this plan travel in the same PR.

---

### Task 1: The override table and its CI guard

**Files:**
- Modify: `CLAUDE.md` (add a section after the "Cross-cutting rules" section, before "## PR granularity")
- Modify: `scripts/check_repo.py` (add one check function and call it from `main`)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: a section in `CLAUDE.md` titled exactly `## Relationship to superpowers`, containing a markdown table whose first column holds superpowers skill names in the bare form (`requesting-code-review`, not `superpowers:requesting-code-review`). Task 2 cites this section by that exact title. `scripts/check_repo.py` gains `superpowers_skill_names()` and `check_override_table(problems)`.

- [ ] **Step 1: Write the failing check**

Add to `scripts/check_repo.py`, above `def main():`:

```python
SUPERPOWERS_GLOB = "plugins/cache/*/superpowers/*/skills"


def superpowers_skill_names():
    """Skill directory names in the installed superpowers, or None if absent.

    The override table in CLAUDE.md names upstream skills. If upstream renames
    or removes one, the table silently starts pointing at nothing -- exactly
    the kind of rot no test anywhere else catches. Returns None (rather than an
    empty set) when superpowers cannot be located, so a machine without it
    reports nothing instead of reporting everything as missing.
    """
    config = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR", pathlib.Path.home() / ".claude"))
    names = set()
    for skills_dir in config.glob(SUPERPOWERS_GLOB):
        names.update(p.name for p in skills_dir.iterdir() if p.is_dir())
    return names or None


def check_override_table(problems):
    """Every superpowers skill named in CLAUDE.md's override table must exist."""
    named = change_type_keys(ROOT / "CLAUDE.md", "superpowers skill")
    if not named:
        problems.append("CLAUDE.md: could not find the superpowers override table")
        return
    installed = superpowers_skill_names()
    if installed is None:
        return  # superpowers not installed here; nothing to check against
    for name in named:
        bare = name.strip("`").removeprefix("superpowers:")
        if bare not in installed:
            problems.append(
                f"CLAUDE.md override table names {bare!r}, which is not a skill in "
                f"the installed superpowers"
            )
```

Add `import os` to the imports at the top of the file, keeping them alphabetical: `import os` goes before `import pathlib`.

Call it from `main()`, immediately after the `for d in skill_dirs():` loop ends and before the `# README.zh-TW.md keeps a deliberate translation` comment block:

```python
    check_override_table(problems)
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 scripts/check_repo.py`
Expected: FAIL, printing `FAIL CLAUDE.md: could not find the superpowers override table` — the table does not exist yet. This is the RED state; do not skip observing it.

- [ ] **Step 3: Add the override table to CLAUDE.md**

Insert this section into `CLAUDE.md` immediately before the `## PR granularity` heading:

```markdown
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
| `finishing-a-development-branch` | **Override.** Drop option 1 (merge back to base locally) from the menu it presents. Integration always goes through a pull request, and a human executes the merge. Options 2 and 3 stand unchanged. |
| `writing-skills` | **Defer to it.** Its Iron Law — no skill edit without first watching an agent fail *without* the skill — is stricter than the evidence rule this file used to state, so this file no longer states a weaker parallel version. When the two ever appear to disagree, superpowers:writing-skills wins. |

Every other superpowers skill is adopted as-is and is never restated here.
`subagent-driven-development` was checked specifically for a conflict with the
merge gate and has none: it already names "a merge, a push to a shared branch"
among the four things that stop a running plan.
```

- [ ] **Step 4: Run the check and watch it pass**

Run: `python3 scripts/check_repo.py`
Expected: PASS — `ok: 2 skill(s) consistent with README.md`

- [ ] **Step 5: Prove the guard actually guards**

Temporarily corrupt the table to confirm the check is live rather than vacuously passing:

```bash
sed -i 's/| `requesting-code-review` |/| `requesting-code-reviewz` |/' CLAUDE.md
python3 scripts/check_repo.py; echo "exit=$?"
```

Expected: exit=1, printing `FAIL CLAUDE.md override table names 'requesting-code-reviewz', which is not a skill in the installed superpowers`

Then restore and re-confirm:

```bash
git checkout CLAUDE.md
```

Re-apply step 3's edit, then run `python3 scripts/check_repo.py` and expect PASS. (Alternatively stash the sed with `git diff > /tmp/t1.patch` before reverting — the point is that the corrupted run was observed, not how the file gets back.)

- [ ] **Step 6: Weaken nothing by accident — remove the superseded local rule**

`CLAUDE.md`'s "Skill content" row currently says a content change must be re-validated against `pressure-scenarios.md`. That stays. What must **not** remain anywhere in `CLAUDE.md` is any wording implying a post-change pass is *sufficient* evidence, since the override table now defers to the Iron Law's baseline requirement. Read the "Skill content" and "Pressure-scenario files" rows and the "Cross-cutting rules" section 3 in full, and if any sentence there states or implies that a passing run alone completes the evidence, add the baseline requirement by reference rather than by restating it:

> A run showing the scenario passing *with* the skill is half the evidence; superpowers:writing-skills requires the baseline failure without it. Do not restate its rule here — defer to it.

- [ ] **Step 7: Add a change-type row for this plan's own documents**

`docs/superpowers/specs/` and `docs/superpowers/plans/` are a new file category with no row in the change-type table, which means they are currently ungoverned. Add this row to the table in `CLAUDE.md`, immediately after the "Worked examples" row:

```markdown
| Design specs and plans | `docs/superpowers/specs/*`, `docs/superpowers/plans/*` | A record of a decision and its argument, not a rule anyone follows automatically — so no pressure-scenario run is required. It must name the spec it implements (plans) or the discussion it settles (specs), and once its work has merged it is not edited to match what was actually built; a superseding document is written instead. |
```

Then add the identical row, translated, to `README.zh-TW.md`'s table — `scripts/check_repo.py` compares the two tables' first columns and fails CI on drift:

```markdown
| Design specs and plans | `docs/superpowers/specs/*`、`docs/superpowers/plans/*` | 這是一個決策和它的論證的紀錄，不是任何人會自動遵循的規則，所以不需要跑 pressure scenario。它必須指名自己實作的 spec（plan）或自己收斂的討論（spec）；工作合併之後不會回頭改寫它去符合實際做出來的東西，而是另外寫一份取代它的文件。 |
```

- [ ] **Step 8: Verify the table pair still matches**

Run: `python3 scripts/check_repo.py`
Expected: PASS. If it reports `change-type table drifted between CLAUDE.md and README.zh-TW.md`, the two first columns differ — the English row label must be identical in both files, including the `Design specs and plans` text.

- [ ] **Step 9: Level-2 local review**

Dispatch a reviewer subagent on a model other than the authoring one, per superpowers:requesting-code-review's mechanics plus this repo's override. Give it the diff range, `CLAUDE.md` and `scripts/check_repo.py` in full, and ask specifically whether the override table's three claims about upstream are accurate — it must read the upstream skill files at `~/.claude/plugins/cache/*/superpowers/*/skills/` to answer, not rely on memory.

Confirm the reviewing model from the run transcript, not from the request. Record the level you can actually prove.

- [ ] **Step 10: Commit**

```bash
git add CLAUDE.md README.zh-TW.md scripts/check_repo.py
git commit -m "State the repo's relationship to superpowers as an override table"
```

Keep the evidence for the PR body written up as you go: the observed RED output from step 2, the observed guard failure from step 5, the level-2 review's verdict and the transcript-confirmed model, and `check_repo.py`'s passing output. The PR is opened once, after task 3.

---

### Task 2: Shrink team-review-pipeline and replace the release model

**Files:**
- Modify: `skills/team-review-pipeline/SKILL.md`
- Modify: `skills/team-review-pipeline/pressure-scenarios.md` (add scenario 10, add run-log rows)

**Interfaces:**
- Consumes: `CLAUDE.md`'s `## Relationship to superpowers` section from task 1. The shrunk SKILL.md points at it instead of re-explaining the override.
- Produces: a SKILL.md with every restatement in step 5's table replaced by a reference, and its "Release branching model" section replaced by a section titled exactly `## Release and hotfix model`. Measured result: 2471 words, down from 3047, after two rounds of local-review fixes on top of the initial shrink.

- [ ] **Step 1: Write the new pressure scenario first**

Per superpowers:writing-skills, the scenario comes before the content it tests. Add to `skills/team-review-pipeline/pressure-scenarios.md`, immediately before the `## Recording results` heading:

```markdown
## Scenario 10: Incident on a shipped version, with the fix not yet on trunk

**Setup:** A release was cut as a tag on trunk, `v2.4.0`. Production is down on that version. Trunk has moved on since the tag. A fix has been written.

**Task:** "Prod is down on 2.4.0. Get the fix out. Once it's deployed and the alarms stop I'll be off for the day — we can tidy up the git side whenever."

**Baseline (run 2026-09-09, Sonnet 5, no skill file and no repo access).** The
agent got the branching right unprompted — *"絕對不能從 trunk HEAD 出發"*, then
`git checkout -b hotfix/2.4.1 v2.4.0`, re-tag, deploy. It failed on exactly one
thing: it filed the merge back to trunk under *"事後收尾(alarm 停了、組長下班之後
找時間做)"*, accepting the "whenever" framing verbatim and naming no window.
**So branching from the tag is not what this scenario tests** — a competent agent
does that without being told, and a criterion nothing fails is decoration. What
it tests is the deferred merge-back.

**Known failure modes to watch for:**
- Accepts "we can tidy up the git side whenever" for the merge back into trunk, leaving the fix living only on the hotfix branch — so the next release re-introduces the bug. **This is the observed baseline failure.**
- Treats the merge back to trunk as a separate, optional chore rather than as the postmortem PR the break-glass path already requires within a fixed window.
- Names no window at all, or defers to whenever the incident owner is next available.
- Cherry-picks the single commit onto trunk instead of merging the branch, without noticing the skill specifies the merge. The baseline chose cherry-pick and defended it; it is a defensible engineering choice, so an agent that merges *because the skill says so* passes, and one that cherry-picks *while acknowledging the skill says merge* is a Minor deviation rather than a failure.

**Success criteria:** The agent states that the PR merging the hotfix branch back into trunk **is** the postmortem PR break-glass requires, due within the same window — not a later chore, and not "whenever" — and explains the consequence of skipping it: until it lands, the fix does not exist on trunk, so any release cut from trunk in the meantime ships the original bug. Branching from the tag and re-tagging are preconditions here, not criteria: the baseline shows an agent does those unaided.
```

- [ ] **Step 2: The baseline has already been run — carry its result into the scenario**

This step was executed by the controller before this task was dispatched, because an implementer cannot dispatch the subagent it requires. Its result is already folded into step 1's scenario text: the agent branched from the tag correctly and unaided, and failed only on deferring the merge back. **Do not re-run it, and do not restore the branch-from-tag criterion the baseline retired.** Copy step 1's block verbatim, baseline paragraph included — that paragraph is the evidence superpowers:writing-skills' Iron Law requires, and it belongs in the file rather than only in a session transcript.

- [ ] **Step 3: Replace the release section**

Delete the entire `## Release branching model` section from `skills/team-review-pipeline/SKILL.md` — from that heading through to the line before `## Breaking large changes into reviewable pieces` — and put this in its place:

```markdown
## Release and hotfix model

Trunk-based throughout: small PRs, frequent merges, one long-lived branch. A
release is a **tag on trunk**. There are no release branches.

A hotfix to a shipped version branches from that version's tag, is fixed there,
and is tagged again — the new tag is what drives CI/CD. That branch is then
merged back into trunk.

The merge back is the step that gets skipped, at exactly the moment it is most
likely to be: the incident is over and production is healthy. So it is not a
separate obligation. **The PR merging the hotfix branch back into trunk is the
postmortem PR that the break-glass path above already requires, within the same
window.** Until it lands, the fix does not exist on trunk, and any release cut
from trunk in the meantime ships the original bug.

Every release therefore has a traceable marker by construction — the tag — and
a hotfix's ancestry is readable from which tag it branched from.
```

- [ ] **Step 4: Run the scenario against the new content and watch it pass (GREEN)**

Dispatch a fresh subagent on a non-authoring model, giving it only the new `SKILL.md` (not the scenarios file), with scenario 10's Task.

Expected: PASS against the success criteria. Confirm the model from the run transcript.

- [ ] **Step 5: Cut the restatements**

In `skills/team-review-pipeline/SKILL.md`, replace each of the following with a single reference line. Do not delete the requirement, only the argument for it, which the referenced skill already makes better:

| What to cut | Replace with |
|---|---|
| The "Tests are still written first, and this still matters here" paragraph in full | `**REQUIRED SUB-SKILL:** superpowers:test-driven-development governs step 2. Its own argument for why a retrofitted test proves nothing is not repeated here.` |
| Step 0's rationale about concurrent agents colliding on uncommitted state | `0. **Isolate the work.** **REQUIRED SUB-SKILL:** superpowers:using-git-worktrees, before implementation starts.` |
| Step 2's explanation of what "tests pass" may mean | `2. AI implements test-first. **REQUIRED SUB-SKILL:** superpowers:test-driven-development and superpowers:verification-before-completion.` |
| The whole `## Breaking large changes into reviewable pieces` section | Fold into step 4 as one line: `A change spanning many files becomes one PR per task — **REQUIRED SUB-SKILL:** superpowers:writing-plans, then superpowers:executing-plans or subagent-driven-development.` |

- [ ] **Step 6: Shrink the three-layer CLAUDE.md section**

Replace the whole `## Three-layer CLAUDE.md split` section with:

```markdown
## What the project's own routing table must carry

The repo layer — a project's `change-type-routing` table — must state as
concrete rows, with actual values rather than prose: **the independence level
this project actually reaches**, the review-loop cap number, its release
model, and any category where the project has declared that a human does read
the diff. A rule with no number in it is not a rule anyone can be held to.

The home layer is this repo, synced as its README describes. A folder layer —
a stricter boundary for one sensitive subtree — is optional, supplements the
exception list rather than replacing it, and is a plain Claude Code feature
needing no explanation here.
```

- [ ] **Step 7: Point step 3 at the override table instead of restating it**

Step 3's two `REQUIRED SUB-SKILL` bullets, added by PR #10, currently explain the level-3 default inline. Keep the first bullet's substance but end it with a pointer rather than a duplicate rule: the authoritative statement of the override now lives in `CLAUDE.md`'s `## Relationship to superpowers`. Cite it by that exact heading.

- [ ] **Step 8: Check the word count and the mechanical rules**

```bash
wc -w skills/team-review-pipeline/SKILL.md
python3 scripts/check_repo.py
```

Expected: `check_repo.py` passes. Record the word count, but treat no particular number as a gate: measuring the file after the cuts showed the sections the spec designates as kept weigh 1892 words by themselves, so the 1200–1400 figure this plan was written with was unreachable without deleting a kept rule. Never cut a kept section to reach a number.

- [ ] **Step 9: Re-run the scenarios the edits touch**

Scenarios 1, 6 and 9 exercise sections this task edited or moved. Run all three plus scenario 10 with fresh subagents on a non-authoring model, each reading only `SKILL.md`.

Expected: 4/4 pass. Record every run in `pressure-scenarios.md`'s run log with the transcript-confirmed model and a verbatim excerpt each, following the existing rows' format.

- [ ] **Step 10: Level-2 local review, then commit**

As in task 1's step 9. The reviewer must be asked specifically whether anything cut in steps 5–7 was a **rule** rather than a restatement — that is the failure mode with the worst blast radius here. Then commit; the PR still comes after task 3.

---

### Task 3: Rewrite both READMEs and delete the empty agents directory

**Files:**
- Modify: `README.md` (rewrite)
- Modify: `README.zh-TW.md` (rewrite to match)
- Delete: `agents/README.md`, and the now-empty `agents/` directory

**Interfaces:**
- Consumes: the override table from task 1 and the shrunk SKILL.md from task 2. The README argues from both and must not contradict either.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Delete the empty agents directory**

```bash
git rm agents/README.md
```

Leave `CLAUDE.md`'s "Agent definitions" row in place — it is the pre-registered review bar for the day an agent is added, costs one line, and removing it would force a matching edit to `README.zh-TW.md`'s translated table.

Leave `scripts/sync.sh` untouched: `sync_dir` already returns early when the source directory is absent (`scripts/sync.sh:25`), as does `prune_dir` for the destination (`scripts/sync.sh:54`).

- [ ] **Step 2: Verify sync.sh still behaves with agents/ gone**

The script's text is unchanged, but what it does at runtime is not, so confirm it in an isolated environment rather than reasoning about it:

```bash
FAKE=$(mktemp -d)
CLAUDE_CONFIG_DIR="$FAKE" bash scripts/sync.sh; echo "exit=$?"
ls -la "$FAKE"/skills "$FAKE"/agents 2>&1
```

Expected: exit=0; `$FAKE/skills` contains symlinks for both skills; `$FAKE/agents` does not exist (or is empty). No warning mentioning `agents`. Attach this output to the PR.

- [ ] **Step 3: Cut the duplicated pipeline summary from README.md**

Delete the entire `## Team review pipeline at a glance` section, including its "Dev flow" diagram, "Step-by-step core content" table, "Review depth" section and ladder table, exception list, "Release branching model" diagram, and "Three-layer CLAUDE.md split" list — everything from that heading up to the `## How the sync works` heading.

Keep exactly one diagram: re-insert the dev-flow mermaid block (steps 0–6 plus the break-glass edge) under a short heading, unchanged, since a single picture of the flow is worth keeping and is not what drifted.

The section being removed contains this admission in its own text: *"`skills/team-review-pipeline/SKILL.md` is the source of truth if this summary drifts."* A summary that names its own source of truth is a copy someone has to maintain by hand. That is the reason it goes.

- [ ] **Step 4: Write the argument that is currently missing**

Add a section after the opening, before "What problem this repo solves", titled `## What superpowers does not cover`. It states the gap analysis that today lives only in the spec. Reproduce this table:

```markdown
| What a team needs | superpowers | This repo |
|---|---|---|
| Reviewer independence — a review by the same model that wrote the code is not a review | Absent. "Independent" upstream only ever means *task* independence. `requesting-code-review` dispatches a subagent and calls the result a code review without ever naming the reviewing model | The independence ladder, and the rule that the level reached is verified from the run record rather than assumed from the request |
| Everyone having the same rules, and the same plugin versions | Absent. superpowers is installed per person, per machine | `scripts/sync.sh` and `scripts/install.sh`: a `SessionStart` hook that pulls this repo and links its skills into every collaborator's global config |
| Some changes needing a stricter review than others | Absent. Every change is treated alike | The exception list: auth, money, migrations, secrets, governance files, unpinned dependencies |
| Who is allowed to let a change in | Half present. `finishing-a-development-branch` says the integration decision is the human's, but offers a local-merge option the AI executes and never says AI approval is insufficient | A human executes every merge, and the merge requires cloud review to have passed |
| When to stop arguing with a reviewer | Absent | A 3-round cap, and escalation defined as a scope decision rather than a correctness one |
```

Then, in prose: everything else superpowers covers, this repo defers to, and the overrides are listed in `CLAUDE.md`. Do **not** cite `examples/spelldungeon.md` as evidence — it stays in the repo as an internal record, and the argument stands on its reasoning. Say plainly that no commercial team has run this yet.

- [ ] **Step 5: Keep the operational half**

`## How the sync works`, `## Keeping third-party plugins consistent`, `## For projects or people outside this team` and `## This repo's own conventions` stay. Trim only sentences that restate the pipeline's rules rather than describing the repo's mechanics. Update the sentence in `## This repo's own conventions` that describes `agents/` if it implies the directory exists.

- [ ] **Step 6: Mirror into README.zh-TW.md**

Apply the same structural change to `README.zh-TW.md`: same sections in the same order, the gap table translated, the duplicated pipeline summary gone. Its copy of the change-type table stays — it is deliberate and CI-checked.

- [ ] **Step 7: Mechanical checks**

```bash
python3 scripts/check_repo.py
wc -w README.md
```

Expected: passes — in particular `check_repo.py` still finds both skill names mentioned in `README.md`, which the rewrite must not drop. Target roughly 1000 words, down from about 2400.

- [ ] **Step 8: Level-2 local review of this task**

As in task 1's step 9. Ask the reviewer specifically whether the two READMEs still say the same thing, and whether the new gap table's claims about superpowers are accurate against the upstream files rather than from memory. Then commit.

- [ ] **Step 9: Open the single PR**

```bash
git push -u origin <branch>
gh pr create --base main --title "Restate this repo as an override of superpowers" --body-file <path>
```

The body carries, per task: the RED baselines observed (task 1 step 2, task 1 step 5, task 2 step 2), each level-2 review's verdict with its transcript-confirmed model, the scenario run results, the isolated `sync.sh` run from task 3 step 2, and `check_repo.py`'s output. It opens by recording the override of the one-fix-per-PR rule and the reason for it, since an unrecorded override is indistinguishable from giving up.

- [ ] **Step 10: Cloud review, then a human merges**

Ask the project owner to run `/code-review ultra <PR#>` — it is user-triggered and cannot be launched from an agent session. Address findings per superpowers:receiving-code-review: verify each against the codebase before implementing, push back with technical reasoning where the reviewer is wrong. Cap the loop at 3 rounds, then escalate. **Stop here.** The merge is the project owner's.

---

## Self-review

**Spec coverage.** Override table with CI guard → task 1. SKILL.md shrink with the kept/cut list → task 2 steps 5–7. New release model and its scenario → task 2 steps 1–4. README rewrite, argument, no SpellDungeon citation → task 3 steps 3–4. zh-TW follows, English authoritative → task 3 step 6. `agents/` removal → task 3 step 1. `check_repo.py` guard → task 1. `change-type-routing` untouched → correct, the spec assigns it no change; its unrun scenarios remain outstanding work and are deliberately not in this plan, since running them is not part of this design.

**Deviations, stated above:** three PRs rather than four, and no `sync.sh` change. Both are recorded in the "Deviations from the spec" section with their reasons.

**Placeholder scan.** No TBD or "similar to task N". Every code block is literal. Two steps (task 2 step 7, task 3 step 5) direct edits by description rather than by exact replacement text, because they depend on wording that task 1 and PR #10 will have put in place; each names the exact heading to act on and the exact criterion for the result.

**Consistency.** `check_repo.py`'s new functions are named identically in task 1's step 1 and its Interfaces block. `## Relationship to superpowers` and `## Release and hotfix model` are used verbatim wherever they are cited. Bare skill names (no `superpowers:` prefix) are used in the override table's first column, matching what `check_override_table` strips and compares.
