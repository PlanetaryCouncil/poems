#!/usr/bin/env python3
"""Rebuild index.html from the plain text. Run after editing the poems.

  python3 build.py

The text file is the source of truth; this is the only thing allowed to
derive from it. Keeping the page hand-edited would recreate exactly the
two-sources-of-truth problem the JSON copy was deleted for.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
TXT = ROOT / "haiku-command-line-poems.txt"
OUT = ROOT / "index.html"


def main():
    poems = [p.splitlines() for p in TXT.read_text().strip().split("\n\n")]
    tiles = "\n".join(
        '    <figure class="poem">' +
        "".join("<span>" + l.replace("&", "&amp;").replace("<", "&lt;")
                + "</span>" for l in poem) + "</figure>"
        for poem in poems)
    html = OUT.read_text()
    html = re.sub(r'(<div class="grid">\n).*?(\n  </div>)',
                  lambda m: m.group(1) + tiles + m.group(2), html, flags=re.S)
    html = re.sub(r"never reused\. \d+ of them\.",
                  f"never reused. {len(poems)} of them.", html)
    OUT.write_text(html)
    print(f"rebuilt index.html from {len(poems)} poems")


if __name__ == "__main__":
    main()
