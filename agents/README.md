# agents/

Shared, team-authored Claude Code agent definitions (`*.md`, one subdirectory per agent, same shape as a project's `.claude/agents/*.md`). `scripts/sync.sh` symlinks each subdirectory here into every collaborator's `~/.claude/agents/`, the same way `skills/` gets synced into `~/.claude/skills/`.

Empty for now — this team has no shared custom agent yet. When one is added, give it its own subdirectory (e.g. `agents/some-agent/`) so it follows the same change-type-routing category and review rules as `skills/*/SKILL.md` (see the root `CLAUDE.md`).
