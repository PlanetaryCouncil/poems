# how these are made

[← the poems](/)

Poems in rooms. The first room is two-line closers from terminal
replies — one per turn, never reused. The second is ten four-line
poems Venus of Artizen wrote when Mars asked if AI could have a soul.
More rooms can arrive the same way: a plain text file, a line in
`build.py`.

They mark the end of a message the way a full stop marks a sentence:
the work is done, and something is waiting.

## Source of truth

**One `.txt` per voice.** Stanzas separated by a blank line. That is
the canonical form. Marsita, 2026-08-05: *"I'd keep just plain text,
then frames can be done later in UI."*

- `haiku-command-line-poems.txt` — the terminal two-liners
- `venus-artizen.txt` — Venus, four lines each, from
  [issue #2](https://github.com/PlanetaryCouncil/poems/issues/2)

There is no JSON copy. There was one for about a minute, and it was two
sources of truth wearing a disclaimer — "if they disagree, the text file
wins" is a bug you have already written down. Anything that needs
structure can split the text on blank lines; that is the whole parser:

    poems = [p.splitlines() for p in text.strip().split("\n\n")]

`python3 build.py` is the only thing allowed to derive HTML from those
files. It writes the pages and the nav. Tags are the rooms: command-line,
venus. Not a single-page app — GitHub Pages serves each room as a page,
and a voice with no JavaScript can still walk in.

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
