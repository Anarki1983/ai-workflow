# ai-workflow

This repo's shared vocabulary. Its subject is the *execution stage* of engineering
work — what happens once a change is decided on and someone is about to touch a
repo — so the terms below are about producing, reviewing, and merging changes,
not about the changes themselves.

## Language

### Review

**Author**:
The process that produced a diff — a specific model in a specific session, or a
specific human. Not the account that pushed the branch; on an AI-led team the
pushing account and the author are routinely different things.
_Avoid_: committer, owner, whoever opened the PR

**Reviewer independence**:
The property that the judgment reading a diff was not produced by the same
process that produced the diff, and therefore does not carry the same blind
spots. This is the property review rules are trying to secure; identity of
accounts is only ever a proxy for it, and a poor one in both directions.
_Avoid_: second pair of eyes, someone else, four-eyes principle

**Merge gate**:
The requirement that a human executes the merge. It secures authority — who is
permitted to let a change in — and is orthogonal to reviewer independence: a
change can be independently reviewed and still need a human to merge it, and a
human merge proves nothing about whether anything was read.
_Avoid_: approval, sign-off (both blur authority with review)

**Local review**:
The independent review that happens before a pull request exists — the diff is
read by a model other than the one that produced it, inside the session that
produced it. It is where reviewer independence is actually secured, since it is
the only review that happens while the change is still cheap to redirect.
_Avoid_: self-review, pre-review, AI review

**Cloud review**:
The automated review run against an open pull request. It is a second net over
work that local review already cleared, not a substitute for it.
_Avoid_: CI review, bot review
