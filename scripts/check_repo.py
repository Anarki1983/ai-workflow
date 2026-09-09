#!/usr/bin/env python3
"""Repo self-consistency checks. Run by CI and safe to run by hand.

These check the things that go stale silently in a prose repo: a skill added
without being mentioned in the README, a frontmatter description that drifts
back into summarising the workflow, a skill with no scenarios to validate it
against. Exits non-zero with one line per problem.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def skill_dirs():
    root = ROOT / "skills"
    return sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


def main():
    problems = []
    readme = (ROOT / "README.md").read_text()

    for d in skill_dirs():
        name = d.name
        skill = d / "SKILL.md"

        if not skill.is_file():
            problems.append(f"skills/{name}/: no SKILL.md")
            continue

        fm = frontmatter(skill)
        if fm is None:
            problems.append(f"skills/{name}/SKILL.md: no YAML frontmatter block")
        else:
            m = re.search(r"^description:\s*(.+)$", fm, re.M)
            if not m:
                problems.append(f"skills/{name}/SKILL.md: frontmatter has no description")
            elif not m.group(1).strip().startswith("Use when"):
                # superpowers:writing-skills SDO rule: the description states when
                # to trigger the skill, never what its workflow does.
                problems.append(
                    f"skills/{name}/SKILL.md: description must start with 'Use when', got: "
                    f"{m.group(1).strip()[:60]!r}"
                )
            m = re.search(r"^name:\s*(.+)$", fm, re.M)
            if m and m.group(1).strip() != name:
                problems.append(
                    f"skills/{name}/SKILL.md: frontmatter name {m.group(1).strip()!r} "
                    f"does not match its directory"
                )

        if not (d / "pressure-scenarios.md").is_file():
            problems.append(
                f"skills/{name}/: no pressure-scenarios.md — CLAUDE.md requires skill "
                f"content changes to be re-validated against one"
            )

        if name not in readme:
            problems.append(f"skills/{name}/ is not mentioned anywhere in README.md")

    for line in problems:
        print(f"FAIL {line}")
    if not problems:
        print(f"ok: {len(skill_dirs())} skill(s) consistent with README.md")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
