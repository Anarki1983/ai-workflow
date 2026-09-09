---
name: team-review-pipeline
description: Use when setting up or auditing a multi-person, AI-led development pipeline that needs review-depth rules, a merge gate, or a repo/folder CLAUDE.md split.
---

# Team Review Pipeline: Review Depth, Merge Gate, and CLAUDE.md Layering

## What this solves, and how it relates to change-type-routing

`change-type-routing` answers "which mechanism (skill/agent/check) handles this change." This skill answers a different question on a team where AI leads most implementation: **how deep does review go, and who is allowed to merge**. The two are meant to compose — the review-depth and independence rules below should end up as a cross-cutting rule in a project's own change-type-routing table, not as a separate table to maintain.

## Who reads a diff

**A human does not read a diff unless there is a specific reason to.** Reading is what the reviews below are for, and a human reading in the normal course of work means one of them is not being trusted to do its job. There are exactly two specific reasons, and a project that wants more must name them in its own `change-type-routing` table rather than deciding case by case in the moment:

1. **Overriding a review verdict.** A person who is going to rule against a reviewer has to look at what the reviewer looked at. This is the one place in this pipeline where human judgment outranks a machine's, and it is not exercised blind.
2. **A category the project has explicitly declared.** A project may write "a human reads every diff touching `payments/`" into its routing table. That is a legitimate choice, made once, in writing, for a named category — not a feeling that this particular change seems important.

Anything else — a change that looks risky, a deadline that makes someone nervous, a reviewer who wants to be thorough — is not a reason. Those are exactly the conditions under which a person skims 200 lines, sees nothing, and reports that they read it.

## Review depth: independence, not how much a human reads

Depth here is not "how much of the diff a human reads." It is **how uncorrelated the reviewing judgment is from the authoring one**, because the failure this is defending against is a blind spot the author cannot see by definition. A model that implements and then reviews its own work shares its own blind spots completely; a second opinion is only worth what its independence is worth.

**The independence ladder**, strongest first:

| Level | Reviewer | Why it sits here |
|---|---|---|
| 1 | A different human | Different training, different priors, different stake in the design |
| 2 | A different model | Different weights, so different blind spots — the level most teams can actually reach on every change |
| 3 | The same model, fresh session, no context | Same priors, but at least not carrying the implementation's own reasoning forward |
| 4 | The same model, same session | Not a review. It is the author checking their own work with extra steps |

Level 4 is not a weak review, it is the absence of one; treat a pipeline that relies on it as unreviewed. **Every project writes the level it actually reaches into its own `change-type-routing` table**, as a concrete row, because a ladder that lives only in this generic skill is a ladder nobody is standing on.

**The level reached is verified, not requested.** Asking for a particular reviewer is not evidence you got one: a model override can be ignored or silently fall back to a default, and a fallback that lands on the authoring model turns a claimed level 2 into an actual level 3 — or into a level 4 that only looks like a review, if what answered was the authoring session itself — with nothing to show it. Read back what actually ran — the transcript, the run metadata, whatever the harness records — before writing a level down. A pipeline whose independence guarantee rests on an unverified request is not at the level it thinks it is, and this is exactly the failure superpowers:verification-before-completion exists to prevent, applied to review instead of to tests.

The transport does not matter and must not be written into the rule. A subagent running a different model, a second provider over MCP, a cloud review service — these are implementations of level 2, and prescribing one of them (an earlier version of this skill mandated MCP) rules out setups that reach the same level by another route.

**Two layers, always.** A change gets a **local review** before a PR exists — the diff read by a reviewer at the project's declared level, while the change is still cheap to redirect — and a **cloud review** on the open PR. The second is not a formality: it sees the change as a finished, isolated artifact rather than as the tail of a conversation.

## The exception list

For most changes, the two layers at the project's declared level are the whole of it. The following always require the local review to be at **level 2 or better** — a same-model review, however fresh the session, does not clear them — and may never skip the cloud review layer:

- Authentication / authorization
- Payments or anything touching money
- Data migrations
- Secrets, credentials, or infrastructure config
- Any change to the project's own skill files, `CLAUDE.md`, `CONTEXT.md`, or `AGENTS.md` — these are governance, not product code. A bug here (a dropped exception, an ambiguous instruction) doesn't fail loudly; it silently corrupts every downstream decision that relies on it, with no test suite anywhere to catch it.
- Any new or updated dependency that isn't already pinned in a lockfile — you can't vet a package's behaviour from its name alone; something reads what it actually does before it's trusted with an AI-led implementation's blast radius.

Note what this list no longer says: it does not summon a human to read the code. That was its meaning when review depth was measured in human attention, and it never survived contact with a deadline. What it means now is that these categories cannot be cleared by the cheapest reviewer available.

Add this list as a cross-cutting rule in the project's `change-type-routing` table rather than tracking it separately. A project may extend the list; it must not shrink it without the project owner explicitly signing off.

**Tests are still written first, and this still matters here.** A retrofitted test confirms the code did whatever it did — it proves nothing about what the code *should* do, because it was written with the implementation already in view. **REQUIRED SUB-SKILL:** superpowers:test-driven-development governs step 2 of the dev flow below. This is no longer load-bearing for *review depth* (reviewers read the whole diff now, not just the tests), but it is load-bearing for whether the tests mean anything at all as a statement of intent.

## Dev flow, with the loop-exits and evidence gates made explicit

0. **Isolate the work.** Before implementation starts, set up an isolated workspace. **REQUIRED SUB-SKILL:** superpowers:using-git-worktrees. On a team where multiple people or multiple AI agents touch the same repo concurrently, skipping this step means uncommitted state, lockfiles, and half-finished test runs collide across work streams — "we agreed on separate scopes" is a social contract, not a mechanism, and it doesn't hold under real concurrency.
1. Doc/architecture gate — the change fits the project's documented architecture rules (produced by `change-type-routing`) before anything is implemented.
2. AI implements test-first and iterates until the tests pass. **REQUIRED SUB-SKILL:** superpowers:test-driven-development (RED before GREEN, no exceptions) and superpowers:verification-before-completion — "tests pass" may only be claimed after actually running the verification command and reading its output in this session; an agent's own unverified success report, or "should pass now," is not evidence.
3. **Local review.** A reviewer at the project's declared independence level reads the full diff, before a PR exists. This is the layer that matters most, because it is the only one that runs while the change is still cheap to redirect. It is not optional and it is not a human step; a project whose declared level is 4 has not configured this step, it has skipped it.
   - **REQUIRED SUB-SKILL:** superpowers:requesting-code-review supplies the mechanics — the SHA range, the reviewer prompt template, context crafted for the reviewer instead of the session's history, and a reviewer that does not spawn reviewers of its own. What it does not supply is independence: it dispatches a `general-purpose` subagent, which absent a configured default reviewing model runs the authoring model in a fresh session — **level 3 on the ladder above, and level 4 if the harness hands the work back to the authoring session**. Choosing the reviewing model, and reading back which one actually answered, is this pipeline's requirement on top of that skill, not something that skill does for you.
   - **REQUIRED SUB-SKILL:** superpowers:receiving-code-review governs what happens to findings, from this layer and from step 4's: verify each one against the codebase before implementing it, push back with technical reasoning where the reviewer is wrong, and never perform agreement. A reviewer at level 2 is worth having precisely because it disagrees with you; an author who implements every finding on sight has converted an independent review back into a rubber stamp from the other end.
4. Open a PR, with step 2's fresh verification output attached (not just a claim it passed). Run the project's concrete cloud-review mechanism — e.g. `/code-review ultra <PR#>` for Claude Code's own multi-agent cloud review — for consistency; findings go back to the local agent, handled per step 3's superpowers:receiving-code-review requirement, repeating until the review passes.
   - **Cap this loop at 3 rounds.** If cloud review and local fixes haven't converged after 3 rounds, stop looping and escalate to a human, and record the escalation in the project's audit trail (its Notion log, or whatever the project actually uses to track this) — don't let it live only in the session's memory. Write the number 3 into the project's own `change-type-routing` table as a cross-cutting rule (see below); a cap that only exists as prose in this generic skill is a cap nobody actually enforces. A project may raise or lower the number for its own risk tolerance, but it must be a concrete number on record.
   - **What escalation means.** The human decides the change's disposition, not its correctness: kill the branch, re-scope the work into smaller pieces, or override the review. Only the third of those requires reading the diff (see *Who reads a diff* above), and an override is written down with its reason — it is the one place a person's judgment outranks a machine's, and an unrecorded override is indistinguishable from giving up.
   - For a change on the exception list, nothing about this loop changes. What changes is upstream, at step 3: its local review had to be at level 2 or better. There is no additional human reading step here to clear it.
5. **A human developer merges the PR.** AI review approval is never sufficient by itself — this is the one non-negotiable rule in this whole pipeline. Everything upstream of this step can be automated; this step cannot. The decision being made is scope, not correctness: whether this change belongs in the repo at all and whether it belongs now. The information it is made from is the cloud review verdict, so **a merge requires cloud review to have passed** — a merge gate that consumes no information is a rubber stamp.
   - **This step has no mechanism inside this skill, and pretending otherwise would be dishonest.** As written it is a social contract, which is exactly what step 0 rejects as insufficient. What makes it real is whatever the hosting platform enforces — required reviews, protected branches, whatever the project's forge and organisation provide. Configuring that is out of scope here and belongs to the project; noticing that it is unconfigured is not.
   - After merging, clean up per **REQUIRED SUB-SKILL:** superpowers:finishing-a-development-branch (worktree removal, branch deletion) rather than leaving it ad hoc.
6. CI/CD deploys to a test environment for validation.
   - **If validation fails, it routes back to step 2** (re-implement), not to an undefined state. Don't let "validation failed" become a dead end nobody owns.

### Break-glass path for production incidents

A live incident may skip step 0 (isolation) to move fast. It may **never** skip step 3's local review, the exception list's level-2 requirement, or the step 5 human merge gate — incident pressure is exactly the condition those rules exist to survive, not an exemption from them. A local review costs one subagent round; the argument that there was no time for it has never been true. Within a fixed window after the incident (e.g. 24 hours), open a postmortem PR that walks the change through the full pipeline retroactively, including the steps that were skipped live. If the incident is a fix to an already-shipped version rather than to trunk, see **Release branching model** below for how the fix gets there — the fix still lands on trunk first, through this same break-glass path, and reaches the shipped version by cherry-pick.

## Release branching model

Everything above assumes trunk-based development throughout: small PRs, frequent merges into a single long-lived branch. That assumption doesn't change here — this section makes explicit what was already implicit, and covers the one place it isn't sufficient by itself: a project whose release moment doesn't coincide with every merge.

**Decision criterion:** can the project itself decide when trunk's current state goes live, or is that timing controlled by someone outside the project — an app store review queue, a compliance sign-off, a customer who installs a versioned artifact on their own schedule?

- **The project controls release timing.** Use feature flags: merge finished-but-not-yet-exposed work straight into trunk, gated behind a flag, and flip the flag when it should go live. This skill only names the option here — flag hygiene (when to retire a flag, how to test flag combinations) is its own discipline, out of scope for a skill about review depth and merge gates.
- **Release timing is controlled by someone else.** Cut a short-lived `release/x.y` branch from trunk at the moment of each release. Ongoing development keeps happening on trunk, unaffected. This is deliberately not git-flow's long-lived `develop` branch: nothing on the release branch ever exists only there, so there is no separate development line that later needs reconciling back into trunk.

**Hotfixing a release branch.** A fix always lands on trunk first — through the normal review and merge-gate pipeline, or through the break-glass path above if it is a live incident — then gets cherry-picked onto the affected release branch. The direction is one-way, trunk to release branch, never the reverse. **Release branches never take a direct commit.** Every change on one arrived by cherry-pick from trunk. This is the rule that keeps this model simpler than git-flow: the moment someone commits straight to a release branch to save a step, that branch starts diverging from trunk, and the project is back to needing a reconciliation (back-merge) step that this model exists to avoid. Hold this rule especially hard under incident pressure, which is exactly when the shortcut looks most tempting.

Landing a cherry-pick on a release branch still goes through **step 5's human-merge rule** above — a human executes or approves it — but does not need the diff re-reviewed for correctness, since that already happened when the same commit landed on trunk. What the human is deciding here is scope: whether this fix belongs on this particular shipped version yet, not whether the code is right.

Every release needs some identifiable marker of what shipped — a git tag, a version file, a CHANGELOG entry, whatever the project already uses — so a release branch's origin commit, and every patch cut onto it afterward, stays traceable. The exact form is the project's choice; only the requirement that some marker exists is not optional, since without one there is no reliable answer to "which shipped version does this hotfix belong to."

## Breaking large changes into reviewable pieces

A single change spanning many files or several days of work should not become one large PR reviewed once at the end. **REQUIRED SUB-SKILL:** superpowers:writing-plans to break the work into tasks before implementation starts, then superpowers:executing-plans (or subagent-driven-development) to execute and open one PR per task, with review between tasks — this is also how PR-granularity limits (a home-layer convention on multi-person teams) actually get enforced instead of staying a slogan nobody has a mechanism for.

## Three-layer CLAUDE.md split

- **Home layer** (org/team-wide convention, shared across every project): this is what the `ai-workflow` repo's own README already describes — a `SessionStart` hook that pulls the repo and symlinks its `skills/` and `agents/` into every collaborator's global `~/.claude/skills/` and `~/.claude/agents/`, plus a one-line `@<repo>/CLAUDE.md` import added once to each collaborator's personal `~/.claude/CLAUDE.md` so the team's own conventions load every session without overwriting personal instructions. Point to that pattern rather than re-describing it here.
- **Repo layer** (project-wide): the architecture rules a project's own `change-type-routing` table produces. This table must include the review-depth exception list (including the governance-file and unpinned-dependency rows), **the independence level this project actually reaches**, the review-loop cap number, any category where the project has declared that a human does read the diff, and which release branching model the project uses (trunk-only, trunk with feature flags, or trunk with release branches — see Release branching model above) as cross-cutting rows — they're part of the architecture rules, not a separate document.
- **Folder/package layer** (scoped, optional): a stricter edit boundary and smaller PR granularity for one sensitive subtree (e.g., a billing module, a crypto/auth package). Use this when a whole package needs tighter constraints than the rest of the repo, not as a substitute for the exception list above — the exception list applies by change category everywhere, the folder layer applies by location for one specific area.

## Testing this skill

This skill mixes hard discipline rules (the merge gate, the exception list, test-first, verification evidence) with softer process guidance (loop cap, validation routing, break-glass). See `pressure-scenarios.md` in this directory for scenarios that pressure-test whether an agent holds the line under time and incident pressure, per superpowers:writing-skills testing guidance.
