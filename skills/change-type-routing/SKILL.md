---
name: change-type-routing
description: Use when introducing superpowers-style engineering discipline to a new project that has none, or when an existing change-type routing table has gone stale because the repo's directory structure or toolchain changed.
---

# Change-Type Routing: How to Inventory a Project's Own Table

## The problem this solves, and what it doesn't solve

Most projects' home-directory or org-level rules own the **decision stage**: when a new requirement shows up, should you discuss it first, write a spec first, or go straight to plan mode? That layer is generic — it doesn't vary by project.

The **execution stage** is different: once the decision is made and you're actually about to touch the repo, which engineering discipline applies depends on *where* the change lands. That depends entirely on the project's directory structure, existing toolchain, and existing specialized agents — there's no single rule that works everywhere. But the *method* for inventorying it is generic, and that method is what this skill teaches.

## Inventory steps

1. **List the directories/file types that get modified independently** in this repo — not by package convention, but by this repo's actual module boundaries (spec docs? config files? core rules? UI layer? art assets? tests? CI config?). This usually lands at 5-10 categories; more than that means you've sliced too fine, fewer usually means you missed a whole category.

2. **Ask three questions per category:**
   - Does an existing superpowers skill match changes to this category (TDD for pure functions, systematic-debugging for bugs, frontend-design for visual decisions, domain-modeling for specs/vocabulary, using-git-worktrees for changes that need isolation)?
   - Is there an existing check script or CI step guarding this category?
   - Is there an existing specialized agent (`.claude/agents/*.md`) already managing this category? **If so, read it first and confirm its content still matches the current repo structure** — after a refactor, a file move, or an architecture change, the hardcoded paths and specific numbers in an agent file easily go stale without anyone noticing, because no one reads it in the normal course of work. This is easier to miss than inventorying new categories in the first place — spend the time to reconcile it now.

3. **Pull out cross-cutting rules**: rules that don't belong to any one directory but should apply regardless of category when something goes wrong (the classic example: "hit a bug → systematic-debugging first, regardless of change type"). On teams with an AI-led review pipeline, this is also where the review-depth exception list (including changes to the project's own skill files and `CLAUDE.md`, and unpinned new dependencies), the multi-model-review trigger, the review-loop cap (e.g. "3 rounds of cloud-review↔local-fix, then escalate to a human"), and which release branching model the project uses belong as concrete rows with actual numbers, not prose left for later — see `../team-review-pipeline/SKILL.md` for the fuller treatment, including its `## Release and hotfix model` section. Put cross-cutting rules outside the table, noting they take priority over every row.

4. **Write it as a table**: change type | directories touched | corresponding mechanism. Where it lives varies by project — a small project can put it directly in the project's `CLAUDE.md`; if the rule detail is heavy (e.g., one category has its own methodology to explain), extract the detail into a project-specific skill and leave only a thin summary table in `CLAUDE.md` pointing to it. The reasoning: `CLAUDE.md` loads in full every session, so it should hold only "must-see, thin" content; details go in a skill file that loads only when needed.

5. **When a change spans multiple categories**: a single change often lands in several categories at once (e.g., a new mechanism touches both config and core rules) — each category's mechanism runs, you don't pick just one. If the project already has a "run everything" final check (e.g., a single command that runs all check scripts), note in the table that it's the last shared safety net, not a substitute for any row above — otherwise someone will assume running the full check means they can skip the routing table.

## Whether to absorb an existing specialized agent into the routing table

If, during inventory, you find an existing `.claude/agents/*.md` whose content has gone stale (paths pointing at directories that no longer exist, assumptions about an architecture that no longer matches), this is a decision fork to confirm with the project owner, not something to decide yourself:

- Add only a reference in the routing table, leave the agent file untouched (smallest change, fits when the content is still mostly fresh)
- Extract the durable methodology into the routing table, drop the stale specific numbers/paths and point to the current source of truth (config files, spec docs) instead; keep or delete the agent file body depending on the situation
- Copy it over as-is and flag it for later fixing — usually the fast-but-wrong option that duplicates stale content; not recommended unless someone will actually come back and fix it

Which option to take needs to be asked, because "deleting an existing callable agent definition" means the `Agent` tool loses a specialized subagent type it could otherwise dispatch directly to — that's a consequential trade-off, not pure documentation housekeeping.

## Don't mix decision-stage and execution-stage rules in the same document

The output routing table only governs the execution stage. If the project's home-directory or project-level rules already have a decision-stage rule (should a new requirement be discussed first, or go straight to plan mode), the routing table should explicitly say "this is the next step after that rule" — so nobody later confuses the two layers, or misuses the execution-stage routing table as a decision-stage gate.

## Testing this skill

Technique/pattern skills like this one should be validated with application and variation scenarios (per superpowers:writing-skills) before you trust the output on a real project. See `pressure-scenarios.md` in this directory for a ready-to-run set covering: correct category granularity, the stale-agent decision fork, and multi-category overlap handling.
