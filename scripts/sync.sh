#!/usr/bin/env bash
# Invoked by the global SessionStart hook on every Claude Code session.
# Fail-soft by design: no step here may block session start. Idempotent:
# safe to run every session, safe to run manually any time.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
WARNINGS=()

# --- 0. Keep this repo (and this script) fresh before using it ---
# --ff-only is required, not a preference: this runs unattended on every
# collaborator's machine. A plain `git pull` on a checkout that has any local
# commit silently creates a merge commit in a repo whose scripts execute with
# that collaborator's permissions. Refusing to fast-forward and warning is the
# only safe failure here.
if ! git -C "$REPO_DIR" pull --ff-only --quiet >/dev/null 2>&1; then
  WARNINGS+=("ai-workflow git pull could not fast-forward, using local checkout as-is (diverged, dirty, or offline)")
fi

# --- 1. Symlink this repo's own skills/ and agents/ into the global dirs ---
sync_dir() {
  local kind="$1" # "skills" or "agents"
  local src_root="$REPO_DIR/$kind"
  local dst_root="$CLAUDE_DIR/$kind"
  [ -d "$src_root" ] || return 0
  mkdir -p "$dst_root"
  for src in "$src_root"/*/; do
    [ -d "$src" ] || continue
    local name src_abs dst
    name="$(basename "$src")"
    dst="$dst_root/$name"
    src_abs="$(cd "$src" && pwd)"

    if [ -L "$dst" ] && [ "$(readlink -f "$dst" 2>/dev/null)" = "$src_abs" ]; then
      continue # already correct
    fi
    if [ -e "$dst" ] || [ -L "$dst" ]; then
      WARNINGS+=("skipped $kind/$name: $dst already exists and is not ai-workflow's symlink")
      continue
    fi
    ln -s "$src_abs" "$dst" 2>/dev/null || WARNINGS+=("failed to link $kind/$name into $dst_root")
  done
}
# Remove links this repo created for skills/agents it no longer has. Without
# this the sync is add-only: renaming or deleting a skill here leaves a
# dangling symlink in every collaborator's ~/.claude/ forever, and nothing
# ever reports it. Deliberately narrow, because this deletes files unattended
# -- only a symlink whose literal target is inside $REPO_DIR/$kind/ *and* no
# longer resolves is removed. A real directory, another tool's symlink, or a
# live link is never touched.
prune_dir() {
  local kind="$1" # "skills" or "agents"
  local dst_root="$CLAUDE_DIR/$kind"
  [ -d "$dst_root" ] || return 0
  local dst target name
  for dst in "$dst_root"/*; do
    [ -L "$dst" ] || continue
    target="$(readlink "$dst")"
    case "$target" in
      "$REPO_DIR/$kind/"*) ;;
      *) continue ;; # not ours to remove
    esac
    [ -d "$target" ] && continue # still a live skill/agent
    name="$(basename "$dst")"
    if rm -f "$dst"; then
      # Name the target: removing a symlink discards nothing but its name and
      # where it pointed, so saying both makes an unattended deletion a
      # one-command undo (ln -s <target> <dst>) instead of a black box.
      WARNINGS+=("removed stale $kind/$name link (pointed at $target, which no longer exists) — restore with: ln -s $target $dst")
    else
      WARNINGS+=("failed to remove stale $kind/$name link at $dst")
    fi
  done
}

sync_dir skills
sync_dir agents
prune_dir skills
prune_dir agents

# --- 2. Reconcile pinned third-party plugins ---
MANIFEST="$REPO_DIR/scripts/third-party-plugins.json"
if [ -f "$MANIFEST" ] && command -v claude >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  while IFS= read -r line; do
    [ -n "$line" ] && WARNINGS+=("$line")
  done < <(python3 "$REPO_DIR/scripts/sync_plugins.py" "$MANIFEST" 2>/dev/null)
fi

# --- 3. Surface warnings as a single session-start message, if any ---
if [ "${#WARNINGS[@]}" -gt 0 ] && command -v python3 >/dev/null 2>&1; then
  JOINED="$(printf '⚠️ %s\n' "${WARNINGS[@]}")"
  python3 -c "import json,sys; print(json.dumps({'systemMessage': sys.argv[1]}))" "$JOINED"
fi

exit 0
