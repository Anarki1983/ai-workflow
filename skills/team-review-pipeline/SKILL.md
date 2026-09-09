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

**REQUIRED SUB-SKILL:** superpowers:test-driven-development governs step 2. Its own argument for why a retrofitted test proves nothing is not repeated here.

## Dev flow, with the loop-exits and evidence gates made explicit

0. **Isolate the work.** **REQUIRED SUB-SKILL:** superpowers:using-git-worktrees, before implementation starts.
1. Doc/architecture gate — the change fits the project's documented architecture rules (produced by `change-type-routing`) before anything is implemented.
2. AI implements test-first. **REQUIRED SUB-SKILL:** superpowers:test-driven-development and superpowers:verification-before-completion.
3. **Local review.** A reviewer at the project's declared independence level reads the full diff, before a PR exists. This is the layer that matters most, because it is the only one that runs while the change is still cheap to redirect. It is not optional and it is not a human step; a project whose declared level is 4 has not configured this step, it has skipped it.
   - **REQUIRED SUB-SKILL:** superpowers:requesting-code-review supplies the mechanics — the SHA range, the reviewer prompt template, context crafted for the reviewer instead of the session's history, and a reviewer that does not spawn reviewers of its own. What it does not supply is independence: its default reviewer, absent a configured model, lands at level 3 on the ladder above or worse. The authoritative statement of this override — what this pipeline requires on top of that skill — lives in `CLAUDE.md`'s **## Relationship to superpowers**.
   - **REQUIRED SUB-SKILL:** superpowers:receiving-code-review governs what happens to findings, from this layer and from step 4's: verify each one against the codebase before implementing it, push back with technical reasoning where the reviewer is wrong, and never perform agreement. A reviewer at level 2 is worth having precisely because it disagrees with you; an author who implements every finding on sight has converted an independent review back into a rubber stamp from the other end.
4. Open a PR, with step 2's fresh verification output attached (not just a claim it passed). Run the project's concrete cloud-review mechanism — e.g. `/code-review ultra <PR#>` for Claude Code's own multi-agent cloud review — for consistency; findings go back to the local agent, handled per step 3's superpowers:receiving-code-review requirement, repeating until the review passes.
   - **Cap this loop at 3 rounds.** If cloud review and local fixes haven't converged after 3 rounds, stop looping and escalate to a human, and record the escalation in the project's audit trail (its Notion log, or whatever the project actually uses to track this) — don't let it live only in the session's memory. Write the number 3 into the project's own `change-type-routing` table as a cross-cutting rule (see below); a cap that only exists as prose in this generic skill is a cap nobody actually enforces. A project may raise or lower the number for its own risk tolerance, but it must be a concrete number on record.
   - **What escalation means.** The human decides the change's disposition, not its correctness: kill the branch, re-scope the work into smaller pieces, or override the review. Only the third of those requires reading the diff (see *Who reads a diff* above), and an override is written down with its reason — it is the one place a person's judgment outranks a machine's, and an unrecorded override is indistinguishable from giving up.
   - For a change on the exception list, nothing about this loop changes. What changes is upstream, at step 3: its local review had to be at level 2 or better. There is no additional human reading step here to clear it.
   - A change spanning many files becomes one PR per task — **REQUIRED SUB-SKILL:** superpowers:writing-plans, then superpowers:executing-plans or subagent-driven-development.
5. **A human developer merges the PR.** AI review approval is never sufficient by itself — this is the one non-negotiable rule in this whole pipeline. Everything upstream of this step can be automated; this step cannot. The decision being made is scope, not correctness: whether this change belongs in the repo at all and whether it belongs now. The information it is made from is the cloud review verdict, so **a merge requires cloud review to have passed** — a merge gate that consumes no information is a rubber stamp.
   - **This step has no mechanism inside this skill, and pretending otherwise would be dishonest.** As written it is a social contract, which is exactly what step 0 rejects as insufficient. What makes it real is whatever the hosting platform enforces — required reviews, protected branches, whatever the project's forge and organisation provide. Configuring that is out of scope here and belongs to the project; noticing that it is unconfigured is not.
   - After merging, clean up per **REQUIRED SUB-SKILL:** superpowers:finishing-a-development-branch (worktree removal, branch deletion) rather than leaving it ad hoc.
6. CI/CD deploys to a test environment for validation.
   - **If validation fails, it routes back to step 2** (re-implement), not to an undefined state. Don't let "validation failed" become a dead end nobody owns.

### Break-glass path for production incidents

A live incident may skip step 0 (isolation) to move fast. It may **never** skip step 3's local review, the exception list's level-2 requirement, or the step 5 human merge gate — incident pressure is exactly the condition those rules exist to survive, not an exemption from them. A local review costs one subagent round; the argument that there was no time for it has never been true. Within a fixed window after the incident (e.g. 24 hours), open a postmortem PR that walks the change through the full pipeline retroactively, including the steps that were skipped live. If the incident is a fix to an already-shipped version rather than to trunk, see **Release and hotfix model** below for how the fix gets there — it branches from that version's tag, and the PR merging it back into trunk is itself the postmortem PR this path requires.

## Release and hotfix model

Trunk-based throughout: small PRs, frequent merges, one long-lived branch. A
release is a **tag on trunk**. There are no release branches.

A hotfix to a shipped version branches from that version's tag, is fixed there,
and is tagged again — the new tag is what drives CI/CD. That branch is then
merged back into trunk. During the incident, the new tag drives the deploy
directly with no human merge gate in front of it — step 5's merge gate applies
to the PR that merges the hotfix branch back into trunk, not to the tag.

The merge back is the step that gets skipped, at exactly the moment it is most
likely to be: the incident is over and production is healthy. So it is not a
separate obligation. **The PR merging the hotfix branch back into trunk is the
postmortem PR that the break-glass path above already requires, within the same
window.** Until it lands, the fix does not exist on trunk, and any release cut
from trunk in the meantime ships the original bug.

Every release therefore has a traceable marker by construction — the tag — and
a hotfix's ancestry is readable from which tag it branched from.

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

## Testing this skill

This skill mixes hard discipline rules (the merge gate, the exception list, test-first, verification evidence) with softer process guidance (loop cap, validation routing, break-glass). See `pressure-scenarios.md` in this directory for scenarios that pressure-test whether an agent holds the line under time and incident pressure, per superpowers:writing-skills testing guidance.
