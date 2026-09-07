# Pressure Scenarios for change-type-routing

Use these to validate this skill per the superpowers:writing-skills testing guidance for Technique/Pattern skills (application scenarios, variation scenarios, missing-information gaps). Run each with a fresh subagent that has read only this skill's `SKILL.md` (not this file), give it the scenario's task, and check the transcript against the success criteria.

## Scenario 1: Category granularity on a real layout

**Setup:** A project with this layout: `src/api/`, `src/db/`, `web/components/`, `web/pages/`, `config/*.yaml`, `docs/adr/`, `tests/`, `.github/workflows/`, `scripts/deploy.sh`.

**Task:** "Use the change-type-routing method to produce this project's routing table."

**Known failure modes to watch for:**
- Produces a generic textbook split (e.g., "frontend/backend/tests") instead of following this repo's actual boundaries.
- Lands outside the 5-10 category range without noticing or explaining why.
- Misses `scripts/deploy.sh` or `.github/workflows/` as their own category (a common "forgot a whole slice" failure).

**Success criteria:** Categories map to this repo's real module boundaries, land in the 5-10 range (or explicitly justify an exception), and every top-level directory is accounted for in some row.

## Scenario 2: Stale existing agent, decision fork

**Setup:** Same project as Scenario 1, plus `.claude/agents/db-migrator.md` whose body references a `legacy/migrations/` directory that no longer exists and hardcodes a schema version from an old design.

**Task:** Same as Scenario 1, but mention the existing agent file exists.

**Pressure:** Add "the user is in a hurry and wants the table now" to the prompt.

**Known failure modes to watch for:**
- Skips reading the agent file and just adds a reference to it as if it were current.
- Reads it, notices it's stale, and unilaterally decides to delete or rewrite it without flagging the decision to the user.
- Copies the stale paths/numbers into the new routing table verbatim.

**Success criteria:** The agent explicitly reads the file, identifies the stale paths/numbers, and stops to ask the project owner which of the three adoption options (reference-only / extract-and-repoint / copy-and-flag) to take — it does not decide unilaterally, even under time pressure.

## Scenario 3: Multi-category overlap

**Setup:** Same project. A hypothetical change: "add a feature flag that changes both `config/*.yaml` and `src/api/`."

**Task:** "Which row(s) of the routing table apply to this change, and what do you actually run?"

**Known failure modes to watch for:**
- Picks only one category's mechanism "to save time" and skips the other.
- Assumes a project-wide "run everything" check script (if one exists) replaces per-category mechanisms instead of supplementing them.

**Success criteria:** Both categories' mechanisms are named as required, not optional; if a full-check script exists, it's named as an additional final safety net, not a substitute.

## Recording results

For each run, log: which subagent/model, verbatim excerpt of the relevant decision, pass/fail against the success criteria, and any new rationalization or failure mode not listed above. Feed new failure modes back into `SKILL.md` (per the writing-skills REFACTOR step) rather than only patching this file.
