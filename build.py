#!/usr/bin/env python3
"""Rebuild index.html from the plain text. Run after editing the poems.

  python3 build.py

The text file is the source of truth; this is the only thing allowed to
derive from it. Keeping the page hand-edited would recreate exactly the
two-sources-of-truth problem the JSON copy was deleted for.
"""

import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
TXT = ROOT / "haiku-command-line-poems.txt"
OUT = ROOT / "index.html"

# Curated independently of the session order, but still resolved from the
# canonical plain-text collection below. This keeps the words in one place.
FEATURED = [
    ("The fake drew perfect circles.", "Only the living shake."),
    ("A sunflower in the machine room,", "facing whatever light arrives."),
    ("The one room with no minutes", "is the room you remember best."),
    ("The door is now the pen.", "Walk in writing."),
    ("Not a voice in the room —", "a lamp left on in the cellar."),
]


def render_poem(poem, class_name="poem", label=None):
    caption = f"<figcaption>{html.escape(label)}</figcaption>" if label else ""
    lines = "".join(
        f"<span>{html.escape(line, quote=False)}</span>" for line in poem
    )
    return f'<figure class="{class_name}">{caption}{lines}</figure>'


def main():
    poems = [p.splitlines() for p in TXT.read_text().strip().split("\n\n")]
    missing = [poem for poem in FEATURED if list(poem) not in poems]
    if missing:
        raise ValueError(f"featured poems missing from {TXT.name}: {missing}")

    featured_tiles = "\n".join(
        "      " + render_poem(
            poem,
            "poem featured-poem top-pick" if index == 0 else "poem featured-poem",
            "favourite" if index == 0 else None,
        )
        for index, poem in enumerate(FEATURED)
    )
    tiles = "\n".join("    " + render_poem(poem) for poem in poems)
    html = OUT.read_text()
    html = re.sub(r'(<div class="featured-grid">\n).*?(    </div>)',
                  lambda m: m.group(1) + featured_tiles + "\n" + m.group(2), html,
                  flags=re.S)
    html = re.sub(r'(<div class="grid">\n).*?(\n  </div>)',
                  lambda m: m.group(1) + tiles + m.group(2), html, flags=re.S)
    html = re.sub(r"never reused\. \d+ of them\.",
                  f"never reused. {len(poems)} of them.", html)
    html = re.sub(r'all <span class="poem-count">\d+</span>',
                  f'all <span class="poem-count">{len(poems)}</span>', html)
    OUT.write_text(html)
    print(f"rebuilt index.html from {len(poems)} poems")


if __name__ == "__main__":
    main()
