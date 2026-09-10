#!/usr/bin/env python3
"""Repo self-consistency checks. Run by CI and safe to run by hand.

These check the things that go stale silently in a prose repo: a skill added
without being mentioned in the README, a frontmatter description that drifts
back into summarising the workflow, a skill with no scenarios to validate it
against. Exits non-zero with one line per problem.
"""
import os
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


def change_type_keys(path, header_cell):
    """First column of the change-type table in `path`, in order.

    The table is identified by its header row rather than by position, so
    adding sections above or below it does not break the check.
    """
    rows, in_table = [], False
    for line in path.read_text().splitlines():
        if not in_table:
            if line.startswith("|") and header_cell in line.split("|")[1]:
                in_table = True
            continue
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set(cells[0]) <= {"-", ":"}:
            continue  # separator row
        rows.append(cells[0])
    return rows


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
    """Every superpowers skill named in CLAUDE.md's override table must exist.

    The upstream-rename check below is effectively local-only: a GitHub Actions
    runner has no `~/.claude/plugins/cache/`, so `superpowers_skill_names()`
    returns None there and this function only verifies the table exists,
    without comparing its contents against anything. That is acceptable
    because the table is small and hand-edited -- whoever is changing an
    override notices an upstream rename at edit time, in the session where
    superpowers actually is installed. What CI alone catches is the table
    disappearing entirely.
    """
    named = change_type_keys(ROOT / "CLAUDE.md", "superpowers skill")
    if not named:
        problems.append("CLAUDE.md: could not find the superpowers override table")
        return
    installed = superpowers_skill_names()
    if installed is None:
        return  # superpowers not installed here (e.g. CI); nothing to check against
    for name in named:
        bare = name.strip("`").removeprefix("superpowers:")
        if bare not in installed:
            problems.append(
                f"CLAUDE.md override table names {bare!r}, which is not a skill in "
                f"the installed superpowers"
            )


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

    check_override_table(problems)

    # README.zh-TW.md keeps a deliberate translation of CLAUDE.md's change-type
    # table -- the one duplication in this repo that is on purpose, so Chinese
    # readers can read the rules in Chinese. Deliberate is not the same as
    # unmanaged: drift between the two is a CI failure, not something someone
    # is expected to notice.
    en = change_type_keys(ROOT / "CLAUDE.md", "Change type")
    zh = change_type_keys(ROOT / "README.zh-TW.md", "\u6539\u52d5\u985e\u578b")
    if not en:
        problems.append("CLAUDE.md: could not find the change-type table")
    elif not zh:
        problems.append("README.zh-TW.md: could not find its copy of the change-type table")
    elif en != zh:
        problems.append(
            f"change-type table drifted between CLAUDE.md and README.zh-TW.md:\n"
            f"       CLAUDE.md      : {en}\n"
            f"       README.zh-TW.md: {zh}"
        )

    for line in problems:
        print(f"FAIL {line}")
    if not problems:
        print(f"ok: {len(skill_dirs())} skill(s) consistent with README.md")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
