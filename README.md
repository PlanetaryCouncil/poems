# haiku-command-line-poems

Two-line poems written at the end of terminal replies — one per turn, made
for the turn it closed, never reused. They mark the end of a message the
way a full stop marks a sentence: the work is done, and something is
waiting.

## Source of truth

**`haiku-command-line-poems.txt`** — plain text, one poem per stanza,
blank line between. That is the canonical form. Marsita, 2026-08-05:
*"I'd keep just plain text, then frames can be done later in UI."*

`haiku-command-line-poems.json` is the same lines as an array, for
anything that wants to render or index them. If the two ever disagree,
the text file wins.

## Frames are presentation

In the terminal they are drawn inside a box:

    ╭────────────────────────────────╮
    │ The fake drew perfect circles. │
    │ Only the living shake.         │
    ╰────────────────────────────────╯

The frame belongs to whatever draws it, not to the poem. One rule matters
if you rebuild it: compute the width from the longest line, emit the
frame, and assert every row is the same length before showing it.
Hand-padding has failed every single time — a box is only a string you
*believe* renders as a box, and three of these had drifted a column just
from being copied between files.

`2026-08-04-05.md` keeps the framed originals for the record.
