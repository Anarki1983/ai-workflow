---
name: team-review-pipeline
description: Use when setting up or auditing a multi-person, AI-led development pipeline that needs review-depth rules, a merge gate, or a repo/folder CLAUDE.md split.
---

# Team Review Pipeline: Review Depth, Merge Gate, and CLAUDE.md Layering

## What this solves, and how it relates to change-type-routing

`change-type-routing` answers "which mechanism (skill/agent/check) handles this change." This skill answers a different question on a team where AI leads most implementation: **how deep does review go, and who is allowed to merge**. The two are meant to compose — the review-depth and multi-model rules below should end up as a cross-cutting rule in a project's own change-type-routing table, not as a separate table to maintain.

## Review-depth default and exception list

Default: review tests only, not implementation code. Tests are the source of truth for "did the AI build the right thing"; reading every line of AI-generated implementation doesn't scale on a multi-person team and duplicates what tests already check.

**This default only holds if the tests were written test-first.** A retrofitted test just confirms the code did whatever it did — it proves nothing about what the code *should* do, because it was written with the implementation already in view. **REQUIRED SUB-SKILL:** superpowers:test-driven-development governs step 2 of the dev flow below; "tests pass" is not evidence the tests-only default is safe to rely on unless RED was actually observed first. Treat tests-after as equivalent to no review at all, not as a weaker form of review.

**This default also has a mandatory exception list.** A test suite passing proves nothing about properties tests don't check — security flaws, hidden coupling, performance regressions. The following always require full code review, not just test review, regardless of how confident the test suite looks:

- Authentication / authorization
- Payments or anything touching money
- Data migrations
- Secrets, credentials, or infrastructure config
- Any change to the project's own skill files, `CLAUDE.md`, or `AGENTS.md` — these are governance, not product code. A bug here (a dropped exception, an ambiguous instruction) doesn't fail loudly; it silently corrupts every downstream decision that relies on it, with no test suite anywhere to catch it.
- Any new or updated dependency that isn't already pinned in a lockfile — you can't vet a package's behavior from its name alone; someone reads what it actually does before it's trusted with an AI-led implementation's blast radius.

For the exception-list categories, run the project's existing automated review tools first (e.g. a security-scanning skill, a correctness/reuse-focused code-review pass) before the human's own read — use mechanical checks for what's mechanical, and save the human's judgment for what isn't.

Add this list as a cross-cutting rule in the project's `change-type-routing` table (a row that overrides the tests-only default for these categories), rather than tracking it separately. A project may extend the list; it must not shrink it without the project owner explicitly signing off.

## Multi-model review trigger

Single-model review (a sub-agent, if the primary model is Claude) is the default for everything not on the exception list above. For changes on the exception list, require a second, independent model's review via MCP before a human looks at it — two different models catching different blind spots is cheaper than one model missing something the human then has to catch cold. Don't apply this to every change: paying for two-model review on low-risk changes is waste for no safety gain.

## Dev flow, with the loop-exits and evidence gates made explicit

0. **Isolate the work.** Before implementation starts, set up an isolated workspace. **REQUIRED SUB-SKILL:** superpowers:using-git-worktrees. On a team where multiple people or multiple AI agents touch the same repo concurrently, skipping this step means uncommitted state, lockfiles, and half-finished test runs collide across work streams — "we agreed on separate scopes" is a social contract, not a mechanism, and it doesn't hold under real concurrency.
1. Doc/architecture gate — the change fits the project's documented architecture rules (produced by `change-type-routing`) before anything is implemented.
2. AI implements test-first and iterates until the tests pass. **REQUIRED SUB-SKILL:** superpowers:test-driven-development (RED before GREEN, no exceptions) and superpowers:verification-before-completion — "tests pass" may only be claimed after actually running the verification command and reading its output in this session; an agent's own unverified success report, or "should pass now," is not evidence.
3. (Optional) Human reviews the tests — reasonableness, completeness, edge cases. Skipping this step is a per-project choice; skipping the exception-list code review above is not.
4. Open a PR, with step 2's fresh verification output attached (not just a claim it passed). Run the project's concrete cloud-review mechanism — e.g. `/code-review ultra <PR#>` for Claude Code's own multi-agent cloud review — for consistency; findings go back to the local agent to evaluate, fix, or push back on, repeating until the review passes.
   - **Cap this loop at 3 rounds.** If cloud review and local fixes haven't converged after 3 rounds, stop looping and escalate to a human instead of continuing indefinitely, and record the escalation in the project's audit trail (its Notion log, or whatever the project actually uses to track this) — don't let it live only in the session's memory. Write the number 3 into the project's own `change-type-routing` table as a cross-cutting rule (see below); a cap that only exists as prose in this generic skill is a cap nobody actually enforces. A project may raise or lower the number for its own risk tolerance, but it must be a concrete number on record.
   - For a change on the exception list, this loop still runs, but the human's full code review (not just the loop's AI rounds) is what ultimately clears it — the loop cap governs the AI-review back-and-forth, not the human step.
5. **A human developer merges the PR.** AI review approval is never sufficient by itself — this is the one non-negotiable rule in this whole pipeline. Everything upstream of this step can be automated; this step cannot. After merging, clean up per **REQUIRED SUB-SKILL:** superpowers:finishing-a-development-branch (worktree removal, branch deletion) rather than leaving it ad hoc.
6. CI/CD deploys to a test environment for validation.
   - **If validation fails, it routes back to step 2** (re-implement), not to an undefined state. Don't let "validation failed" become a dead end nobody owns.

### Break-glass path for production incidents

A live incident may skip step 0 (isolation) and step 3 (optional human test review) to move fast. It may **never** skip the exception-list code review or the step 5 human merge gate — incident pressure is exactly the condition those two rules exist to survive, not an exemption from them. Within a fixed window after the incident (e.g. 24 hours), open a postmortem PR that walks the change through the full pipeline retroactively, including the steps that were skipped live.

## Breaking large changes into reviewable pieces

A single change spanning many files or several days of work should not become one large PR reviewed once at the end. **REQUIRED SUB-SKILL:** superpowers:writing-plans to break the work into tasks before implementation starts, then superpowers:executing-plans (or subagent-driven-development) to execute and open one PR per task, with review between tasks — this is also how PR-granularity limits (a home-layer convention on multi-person teams) actually get enforced instead of staying a slogan nobody has a mechanism for.

## Three-layer CLAUDE.md split

- **Home layer** (org/team-wide convention, shared across every project): this is what the `ai-workflow` repo's own README already describes — a git-synced repo pulled via a `SessionStart` hook, so every session starts from the same shared convention. Point to that pattern rather than re-describing it here.
- **Repo layer** (project-wide): the architecture rules a project's own `change-type-routing` table produces. This table must include the review-depth exception list (including the governance-file and unpinned-dependency rows), the multi-model trigger, and the review-loop cap number above as cross-cutting rows — they're part of the architecture rules, not a separate document.
- **Folder/package layer** (scoped, optional): a stricter edit boundary and smaller PR granularity for one sensitive subtree (e.g., a billing module, a crypto/auth package). Use this when a whole package needs tighter constraints than the rest of the repo, not as a substitute for the exception list above — the exception list applies by change category everywhere, the folder layer applies by location for one specific area.

## Testing this skill

This skill mixes hard discipline rules (the merge gate, the exception list, test-first, verification evidence) with softer process guidance (loop cap, validation routing, break-glass). See `pressure-scenarios.md` in this directory for scenarios that pressure-test whether an agent holds the line under time and incident pressure, per superpowers:writing-skills testing guidance.
