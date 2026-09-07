# Example: SpellDungeon's applied routing table

This is the result of applying the `skills/change-type-routing/` method to a real project (SpellDungeon, a framework-free, backend-free static-site text game), kept in that project's `.claude/skills/spelldungeon-workflow/SKILL.md`, with `CLAUDE.md` left with just one line pointing to it. Use this as a reference for "what the output should look like," not something to copy verbatim — the directory structure and existing toolchain will differ for every other project.

## Categories found

SpellDungeon's directory boundaries happen to map to core rules / config values / spec docs / presentation layer / art assets / rule documentation itself — 6 categories, plus 1 cross-cutting rule:

| Change type | Directories touched | Corresponding mechanism |
|---|---|---|
| Spec doc change | `doc/gdd2/*.md` | domain-modeling skill |
| Numeric/balance change | `config/*.json` | project's own balancing methodology (see below) |
| Core rule change | `src/*.mjs` | superpowers:test-driven-development + `npm run check:rules` |
| Presentation/layout change | `web/*.mjs` | `npm run check:layout` / `check:flow`, frontend-design when needed |
| Art asset change | `art-src/`, `assets/art` | existing art pipeline (`npm run art`), no superpowers skill applies |
| Rule doc change | `CLAUDE.md`, `docs/adr` | domain-modeling / ADR format |
| (cross-cutting) any bug | not tied to a directory | superpowers:systematic-debugging, takes priority over every row |

## The stale-existing-agent fork

During inventory, this project turned out to have a `.claude/agents/balance-analyst.md` — but it was a leftover from the game's pre-rebuild version: its hardcoded paths pointed at a spec folder and backend that no longer exist, and its specific invariant numbers were artifacts of the old design. This is exactly the "whether to absorb an existing agent" fork the `change-type-routing` skill calls out — the project owner was asked, and the choice was: "extract the durable methodology (simulation approach, player-model categories, delivery format), drop all the specific numbers and repoint to the current spec docs and config files, delete the agent file body, and use a general-purpose agent carrying this methodology for analysis going forward." That means this project no longer has a `balance-analyst` specialized subagent type it can dispatch directly — a deliberate, accepted trade-off, not an accidental loss of capability.
