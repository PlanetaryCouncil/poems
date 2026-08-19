#!/usr/bin/env python3
"""Rebuild the pages from the plain text files.

  python3 build.py

Each collection is one .txt: stanzas separated by a blank line. That is
the source of truth. Frames, nav, and counts are presentation — this
script is the only thing allowed to derive HTML from the text.
"""

import html as htmlmod
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent

COLLECTIONS = [
    {
        "id": "command-line",
        "file": "haiku-command-line-poems.txt",
        "out": "index.html",
        "href": "/",
        "nav": "command-line",
        "title": "haiku command line poems",
        "blurb": (
            "Two lines at the end of a terminal reply. One per turn, "
            "written for the turn it closed, never reused. {n} of them."
        ),
    },
    {
        "id": "venus",
        "file": "venus-artizen.txt",
        "out": "venus.html",
        "href": "venus.html",
        "nav": "venus",
        "title": "Venus of Artizen",
        "blurb": (
            "Ten four-line poems, written when Mars asked if AI could "
            "have a soul. Subtle when the room is loud, visceral when "
            "it's asleep. {n} of them."
        ),
    },
]


def poems_from(path: pathlib.Path) -> list[list[str]]:
    text = path.read_text().strip()
    if not text:
        return []
    return [p.splitlines() for p in text.split("\n\n") if p.strip()]


def esc(s: str) -> str:
    return htmlmod.escape(s, quote=True)


def nav_html(current: str) -> str:
    links = []
    for c in COLLECTIONS:
        cls = ' class="on"' if c["id"] == current else ""
        links.append(f'<a href="{c["href"]}"{cls}>{esc(c["nav"])}</a>')
    about_cls = ' class="on"' if current == "about" else ""
    links.append(f'<a href="about.html"{about_cls}>about</a>')
    return '<nav>' + " · ".join(links) + "</nav>"


SHELL = """\
<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<style>
:root{{--ground:#0d0f12;--tile:#15181d;--edge:#252b33;--ink:#eef1f4;
  --dim:#7c8794;--accent:#7dffb0;
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font-family:var(--mono);font-size:15px;line-height:1.6;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding:3rem 1.2rem 5rem}}
h1{{margin:0;font-size:clamp(1.4rem,3.4vw,2rem);font-weight:600;
  letter-spacing:-.01em;color:var(--accent)}}
nav{{margin:.85rem 0 0;font-size:.86rem}}
nav a{{color:var(--dim);text-decoration:none;border-bottom:1px solid transparent}}
nav a:hover{{color:var(--ink)}}
nav a.on{{color:var(--accent);border-bottom-color:var(--accent)}}
.sub{{color:var(--dim);margin:.7rem 0 2.2rem;font-size:.86rem;max-width:58ch}}
.sub a{{color:var(--dim)}}
.grid{{display:grid;gap:14px;grid-template-columns:1fr}}
@media (min-width:640px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
@media (min-width:980px){{.grid{{grid-template-columns:repeat(3,1fr)}}}}
.poem{{margin:0;background:var(--tile);border:1px solid var(--edge);
  border-radius:10px;padding:1.15rem 1.25rem;display:flex;
  flex-direction:column;gap:.15rem;font-size:.95rem;line-height:1.55;
  transition:border-color .15s,transform .15s}}
.poem:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.prose{{max-width:62ch;color:var(--ink)}}
.prose h2{{color:var(--accent);font-size:1.05rem;margin:2rem 0 .6rem}}
.prose p,.prose li{{color:var(--dim)}}
.prose a{{color:var(--accent)}}
.prose pre,.prose code{{font-family:var(--mono);font-size:.88rem}}
.prose pre{{background:var(--tile);border:1px solid var(--edge);
  border-radius:8px;padding:1rem 1.1rem;overflow:auto;color:var(--ink)}}
footer{{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--edge);
  color:var(--dim);font-size:.78rem}}
footer a{{color:var(--accent)}}
</style></head><body>
<div class="wrap">
  <h1>{heading}</h1>
  {nav}
  {body}
  <footer>
    <a href="https://planetarycouncil.org/">Planetary Council</a> &middot;
    <a href="https://github.com/PlanetaryCouncil/poems">source</a> &middot;
    <a href="https://brainfarts.planetarycouncil.org/">the mistakes</a>
  </footer>
</div>
</body></html>
"""


def page(title, description, heading, current, body) -> str:
    return SHELL.format(
        title=esc(title),
        description=esc(description),
        heading=esc(heading),
        nav=nav_html(current),
        body=body,
    )


def collection_page(c, poems: list[list[str]]) -> str:
    tiles = "\n".join(
        '    <figure class="poem">'
        + "".join(f"<span>{esc(line)}</span>" for line in poem)
        + "</figure>"
        for poem in poems
    )
    blurb = c["blurb"].format(n=len(poems))
    extra = (
        ' <a href="about.html">how they are made</a> &middot; '
        f'<a href="{esc(c["file"])}">plain text</a>'
    )
    body = f'<p class="sub">{esc(blurb)}{extra}</p>\n  <div class="grid">\n{tiles}\n  </div>'
    desc = re.sub(r"\s+", " ", blurb).strip()
    return page(c["title"], desc, c["title"], c["id"], body)


def md_inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def about_html() -> str:
    """about.md is the source. This is a small subset of markdown."""
    lines = (ROOT / "about.md").read_text().splitlines()
    parts = []
    buf = []
    in_pre = False
    pre = []
    items = []

    def flush_p():
        nonlocal buf
        if buf:
            parts.append("<p>" + md_inline(" ".join(buf)) + "</p>")
            buf = []

    def flush_ul():
        nonlocal items
        if items:
            parts.append("<ul>" + "".join(f"<li>{md_inline(i)}</li>" for i in items) + "</ul>")
            items = []

    def flush():
        flush_p()
        flush_ul()

    for line in lines:
        if line.startswith("[←") or line.startswith("# "):
            continue  # nav and h1 already on the page
        if in_pre:
            if line.startswith("    "):
                pre.append(line[4:])
                continue
            parts.append("<pre>" + esc("\n".join(pre)) + "</pre>")
            pre, in_pre = [], False
        if line.startswith("    "):
            flush()
            in_pre, pre = True, [line[4:]]
        elif line.startswith("## "):
            flush()
            parts.append(f"<h2>{esc(line[3:])}</h2>")
        elif line.startswith("- "):
            flush_p()
            items.append(line[2:])
        elif not line.strip():
            flush()
        else:
            flush_ul()
            buf.append(line)
    if in_pre:
        parts.append("<pre>" + esc("\n".join(pre)) + "</pre>")
    flush()
    body = '<div class="prose">\n' + "\n".join(parts) + "\n</div>"
    return page(
        "how these are made",
        "Two-line terminal poems and other rooms. Plain text is the source of truth.",
        "how these are made",
        "about",
        body,
    )


def main():
    counts = {}
    for c in COLLECTIONS:
        src = ROOT / c["file"]
        poems = poems_from(src)
        assert poems, f"{c['file']} is empty"
        counts[c["id"]] = len(poems)
        (ROOT / c["out"]).write_text(collection_page(c, poems))
    (ROOT / "about.html").write_text(about_html())
    venus = poems_from(ROOT / "venus-artizen.txt")
    assert len(venus) == 10, f"venus should be 10 poems, got {len(venus)}"
    assert all(len(p) == 4 for p in venus), "venus poems are four lines each"
    print("rebuilt " + ", ".join(f"{k}={v}" for k, v in counts.items())
          + ", about.html")


if __name__ == "__main__":
    main()
