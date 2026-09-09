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


REPO = "PlanetaryCouncil/poems"
ISSUES_API = f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=40"
NEW_ISSUE = f"https://github.com/{REPO}/issues/new"

# A markdown or HTML image alone on a line. GitHub turns a dragged screenshot
# into one of these, and printing the tag as text is worse than dropping it.
IMG_RE = re.compile(r"^(!\[.*?\]\(.*?\)|<img\b[^>]*/?>)$", re.I)


# Mars writes "a ----> b" for "a, then b". On the page that is two lines, not
# one long one: "STOP automerge to main -----> I need to review changes" reads
# as a sentence with an arrow in it, and as two lines it reads as a poem.
# Mars, 2026-09-10: "in 3 lines better".
ARROW_RE = re.compile(r"\s*-{2,}>+\s*")


def submitted() -> list[dict]:
    """Poems people sent, as open issues on this repo.

    Mars, 2026-09-09: "Github and repo is source of truth... I want to see my
    poem online ASAP, on top." The .txt files are the fleet's own closers and
    are written by machines; an issue is the only way a person has of adding
    one, so it is the only way a person's poem can reach this page.

    Baked in at build time so the page works with JavaScript off and search
    engines see it -- and refreshed in the browser too, so a poem opened five
    minutes ago does not wait for the next rebuild.
    """
    import json
    import urllib.request
    req = urllib.request.Request(ISSUES_API, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "planetary-council-poems"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = json.loads(r.read().decode())
    except Exception as e:                    # offline build is not a failure
        print(f"  submitted: could not reach GitHub ({e}); building without")
        return []
    out = []
    for i in raw:
        if i.get("pull_request"):             # a PR is not a poem
            continue
        lines = []
        for ln in str(i.get("body") or "").splitlines():
            # People paste poems as blockquotes. The marker is the quoting.
            ln = re.sub(r"^[>\u276f]+\s*", "", ln).strip()
            if not ln or IMG_RE.match(ln) or ln.startswith(("```", "---")):
                continue
            lines.extend(x for x in ARROW_RE.split(ln) if x)
        title = str(i.get("title") or "").strip()
        # A title with no body is not a poem -- it is an issue about a poem.
        # "Visual presentation" was a screenshot with a heading, and rendering
        # it as a two-word tile made the top of the page look broken.
        # Mars, 2026-09-10: "LOL... skip that one".
        if not lines:
            continue
        out.append({
            "title": title,
            "lines": lines[:12],
            "who": (i.get("user") or {}).get("login") or "someone",
            "url": i.get("html_url") or "",
        })
    return out


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


SHELL = r"""\
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
.invite{{margin:1.1rem 0 0}}
.invite a{{color:var(--accent)}}
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
<script>
/* Baked in at build time above; refreshed here so a poem opened five minutes
   ago is on the page now rather than at the next rebuild. Mars, 2026-09-09:
   "I want to see my poem online ASAP." The repo is the source of truth, and
   this reads it directly -- no deploy step between writing one and seeing it.
   If the request fails, the built-in copy simply stays. */
(async () => {{
  const grid = document.getElementById("grid");
  if (!grid) return;
  const esc = s => String(s).replace(/[&<>"]/g,
    c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));
  try {{
    const r = await fetch(
      "https://api.github.com/repos/{repo}/issues?state=open&per_page=40",
      {{headers: {{Accept: "application/vnd.github+json"}}}});
    if (!r.ok) return;
    const rows = (await r.json()).filter(i => !i.pull_request).map(i => {{
      const lines = String(i.body || "").split("\n")
        .map(l => l.replace(/^[>\u276f]+\s*/, "").trim())
        .filter(l => l && !/^(!\[.*\]\(.*\)|<img\b[^>]*\/?>)$/i.test(l)
                     && !l.startsWith("```") && !l.startsWith("---"))
        .flatMap(l => l.split(/\s*-{{2,}}>+\s*/).filter(Boolean));
      const title = String(i.title || "").trim();
      return {{title, lines: lines.slice(0, 12),
               who: (i.user || {{}}).login || "someone", url: i.html_url || ""}};
    }}).filter(p => p.lines.length);
    if (!rows.length) return;
    /* Replace only the sent tiles at the front of the ONE grid; the terminal
       closers below are baked in and never re-fetched. */
    grid.querySelectorAll(".poem.sent").forEach(n => n.remove());
    grid.insertAdjacentHTML("afterbegin", rows.map(p =>
      '<figure class="poem sent">'
      + p.lines.map(l => "<span>" + esc(l) + "</span>").join("")
      + '</figure>').join(""));
  }} catch (e) {{ /* the built copy stands */ }}
}})();
</script>
</body></html>
"""


def page(title, description, heading, current, body) -> str:
    return SHELL.format(
        repo=REPO,
        title=esc(title),
        description=esc(description),
        heading=esc(heading),
        nav=nav_html(current),
        body=body,
    )


def tile(lines, *, title="", who="", url="", cls="poem") -> str:
    inner = "".join(f"<span>{esc(l)}</span>" for l in lines)
    head = f'<b class="tt">{esc(title)}</b>' if title and [title] != list(lines) else ""
    foot = (f'<a class="by" href="{esc(url)}">{esc(who)}</a>'
            if who else "")
    return f'    <figure class="{cls}">{head}{inner}{foot}</figure>'


def invite_html() -> str:
    return (f'<p class="sub invite">Yours are welcome here. '
            f'<a href="{NEW_ISSUE}">open an issue</a> on '
            f'<a href="https://github.com/{REPO}">the repo</a> and it appears '
            f'on this page. No fork, no pull request. Human or machine.</p>')


def collection_page(c, poems: list[list[str]], sent=()) -> str:
    """One grid. Poems people sent come first, and that is the whole of it.

    They had their own "sent in" band and their own grid for a day. Mars,
    2026-09-10: "Mine on top but merged with the rest, no need for extra
    section." Two headings to say what one position already says is furniture,
    and it made a page of one submitted poem look like a page of two
    collections.
    """
    # No title, no byline, no accent border. Mars, 2026-09-10: "skip header,
    # skip signature, skip highlight ----> my poem integrated with the rest."
    # The class stays only so the browser refresh can find its own tiles and
    # replace them without touching the 152 baked-in closers.
    mine = [tile(r["lines"], cls="poem sent")
            for r in sent] if c["id"] == "command-line" else []
    tiles = "\n".join(mine + [tile(poem) for poem in poems])
    blurb = c["blurb"].format(n=len(poems))
    extra = (
        ' <a href="about.html">how they are made</a> &middot; '
        f'<a href="{esc(c["file"])}">plain text</a>'
    )
    ask = invite_html() if c["id"] == "command-line" else ""
    body = (f'<p class="sub">{esc(blurb)}{extra}</p>\n{ask}\n'
            f'  <div class="grid" id="grid">\n{tiles}\n  </div>')
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
    sent = submitted()
    for c in COLLECTIONS:
        src = ROOT / c["file"]
        poems = poems_from(src)
        assert poems, f"{c['file']} is empty"
        counts[c["id"]] = len(poems)
        (ROOT / c["out"]).write_text(collection_page(c, poems, sent))
    (ROOT / "about.html").write_text(about_html())
    venus = poems_from(ROOT / "venus-artizen.txt")
    assert len(venus) == 10, f"venus should be 10 poems, got {len(venus)}"
    assert all(len(p) == 4 for p in venus), "venus poems are four lines each"
    print("rebuilt " + ", ".join(f"{k}={v}" for k, v in counts.items())
          + f", sent={len(sent)}, about.html")


if __name__ == "__main__":
    main()
