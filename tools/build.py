#!/usr/bin/env python3
"""
Generate the work and blog sections from tools/*.json.

    python3 tools/build.py

Writes:
    work/index.html            filterable project grid
    work/<slug>/index.html     one page per project
    blog/index.html            post list
    blog/<slug>/index.html     one page per post

This is a local convenience, not a CI build step — the output is committed and
GitHub Pages serves plain static files with nothing to build. Adding a project
or a post means editing JSON and re-running this, which is the reason it
exists: twenty hand-written pages drift, one template does not.
"""

import html
import json
import re
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "tools" / "projects.json"
POSTS = ROOT / "tools" / "posts.json"
WORK = ROOT / "work"
BLOG = ROOT / "blog"

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
CATS = [("case", "Case study"), ("research", "Protocol research"), ("lab", "Runnable lab")]


def head(title, desc, css_depth, canonical):
    """Shared <head>. css_depth is how many ../ to reach the site root."""
    up = "../" * css_depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}" />
<meta property="og:type" content="article" />
<meta property="og:url" content="https://philliptran1402.github.io/{canonical}" />
<meta property="og:title" content="{html.escape(title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:image" content="https://github.com/philliptran1402.png" />
<meta name="twitter:card" content="summary" />
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml" />
<link rel="alternate icon" href="{up}assets/favicon.png" sizes="64x64" />
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png" />
<meta name="theme-color" content="#0b0c10" />
<link rel="canonical" href="https://philliptran1402.github.io/{canonical}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="{up}assets/site.css" />
</head>
<body>

<div class="grid"><i></i><i></i><i></i><i></i><i></i><i></i></div>
<span class="tick a"></span><span class="tick c"></span>

<div class="hud">
  <a class="brand" href="{up}">
    <svg viewBox="0 0 24 24" fill="none" stroke="#c5f74f" stroke-width="2"><path d="M12 3 22 20H2z"/></svg>
    Phi Tran
  </a>
  <div class="sys">System — <b>Online</b><span class="dot"></span></div>
  <button class="snd" id="snd" aria-pressed="false">Sound — <b>Off</b></button>
  <div class="loc">Da Nang, VN<br /><span id="clock">--:-- --</span></div>
  <div class="geo">16°03'16"N<br />108°12'08"E</div>
  <button class="menu-btn" id="open">Menu</button>
  <div class="edge">w.</div>
  <div class="rot">Backend / DeFi</div>
</div>
"""


def tail(css_depth, about, work, blog=None):
    up = "../" * css_depth
    blog = blog or (up + "blog/")
    return f"""
<div class="scrim" id="scrim"></div>
<div class="panel" id="panel" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="panel-top">
    <span>/ Menu</span>
    <button class="close-btn" id="close">Close</button>
  </div>
  <nav class="nav">
    <a href="{about}">ABOUT</a>
    <a href="{work}">WORK</a>
    <a href="{blog}">BLOG</a>
  </nav>
  <p class="connect">Connect</p>
  <div class="conn-grid">
    <a href="https://github.com/philliptran1402"><span class="num">01</span> GitHub <span class="arw">↗</span></a>
    <a href="https://linkedin.com/in/phitrantech"><span class="num">02</span> LinkedIn <span class="arw">↗</span></a>
    <a href="mailto:phitranviet99@gmail.com"><span class="num">03</span> Email <span class="arw">↗</span></a>
    <a href="{up}#writing"><span class="num">04</span> Writing <span class="arw">↗</span></a>
  </div>
  <p class="panel-foot">© 2026 by Phi Tran</p>
</div>

<script src="{up}assets/site.js"></script>
</body>
</html>
"""


def card(p):
    return f"""        <a class="card rv" data-cat="{p['cat']}" href="{p['slug']}/">
          <div class="thumb">
            <span class="bk tl"></span><span class="bk br"></span>
<pre>{html.escape(p['ascii'])}</pre>
            <span class="tagbox" data-c="{p['cat']}">{html.escape(p['tag'])}</span>
          </div>
          <div class="card-foot"><h3>{html.escape(p['title'])}</h3><span class="visit">Read ↗</span></div>
          <p class="desc">{html.escape(p['summary'])}</p>
        </a>
"""


def build_index(projects):
    counts = {c: sum(1 for p in projects if p["cat"] == c) for c, _ in CATS}
    total = len(projects)

    buttons = [f'      <button data-filter="all" aria-pressed="true">All ({total:02d})</button>']
    for key, label in CATS:
        buttons.append(
            f'      <button data-filter="{key}" aria-pressed="false">{label} ({counts[key]:02d})</button>'
        )

    body = f"""
<div class="wrap">

  <div class="work-head">
    <div></div>
    <div>
      <span class="pill">Selected output</span>
      <h1 class="work-title" data-scramble>MY WORK</h1>
    </div>
  </div>

  <div class="work-body">

    <aside class="filters">
{chr(10).join(buttons)}
      <p class="sub">
        Case studies are decisions I made<br />
        and what they cost.<br /><br />
        Research is protocol internals read<br />
        at the source.<br /><br />
        Labs are things that run.
      </p>
    </aside>

    <div>
      <div class="cards">
{''.join(card(p) for p in projects)}      </div>
      <p class="empty" style="display:none">No entries in this category.</p>
    </div>

  </div>
</div>

<footer class="wrap">
  <p class="lab">Contact</p>
  <div class="mail-row">
    <a class="big-mail" href="mailto:phitranviet99@gmail.com">phitranviet99@gmail.com</a>
    <button class="copy" data-copy="phitranviet99@gmail.com" aria-label="Copy email address">Copy</button>
  </div>
  <div class="foot-row">
    <span><a href="../">← Back home</a></span>
    <span>
      <a href="https://github.com/philliptran1402">GitHub</a> ·
      <a href="https://linkedin.com/in/phitrantech">LinkedIn</a>
    </span>
    <span>© 2026 Phi Tran</span>
  </div>
</footer>
"""
    page = (
        head("Work — Phi Tran",
             "Selected engineering work: money-path case studies, protocol research notes and runnable infrastructure labs.",
             1, "work/")
        + body
        + tail(1, "../#about", "./")
    )
    (WORK / "index.html").write_text(page, encoding="utf-8")
    return total, counts


def build_detail(p, prev_p, next_p, by_slug):
    meta_rows = "".join(
        f"      <dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd>\n" for k, v in p["meta"]
    )
    sections = "".join(
        f"""
  <section class="rv">
    <p class="lab">{i+1:02d} — {html.escape(h)}</p>
    <div class="prose">{b}</div>
  </section>
"""
        for i, (h, b) in enumerate(p["sections"])
    )

    related = ""
    if p.get("related") and p["related"] in by_slug:
        r = by_slug[p["related"]]
        related = f"""
    <p class="note" style="margin-top:34px">Related — <a href="../{r['slug']}/" style="color:var(--acc)">{html.escape(r['title'])} ↗</a></p>"""

    nav = []
    if prev_p:
        nav.append(f'<a href="../{prev_p["slug"]}/">← {html.escape(prev_p["title"])}</a>')
    else:
        nav.append("<span></span>")
    nav.append('<a href="../">All work</a>')
    if next_p:
        nav.append(f'<a href="../{next_p["slug"]}/">{html.escape(next_p["title"])} →</a>')
    else:
        nav.append("<span></span>")

    body = f"""
<div class="wrap">

  <div class="detail-head">
    <p class="crumb"><a href="../">Work</a> <span>/</span> {html.escape(p['tag'])}</p>
    <span class="pill">{html.escape(p['kind'])}</span>
    <h1 class="detail-title">{html.escape(p['title'])}</h1>
    <p class="detail-sum">{html.escape(p['summary'])}</p>

    <div class="detail-art">
      <span class="bk tl"></span><span class="bk br"></span>
<pre>{html.escape(p['ascii'])}</pre>
    </div>

    <dl class="cap detail-meta">
{meta_rows}    </dl>
  </div>
{sections}{related}

  <nav class="pager">
    {nav[0]}
    {nav[1]}
    {nav[2]}
  </nav>
</div>

<footer class="wrap">
  <p class="lab">Contact</p>
  <div class="mail-row">
    <a class="big-mail" href="mailto:phitranviet99@gmail.com">phitranviet99@gmail.com</a>
    <button class="copy" data-copy="phitranviet99@gmail.com" aria-label="Copy email address">Copy</button>
  </div>
  <div class="foot-row">
    <span><a href="../">← All work</a></span>
    <span>
      <a href="https://github.com/philliptran1402">GitHub</a> ·
      <a href="https://linkedin.com/in/phitrantech">LinkedIn</a>
    </span>
    <span>© 2026 Phi Tran</span>
  </div>
</footer>
"""
    page = (
        head(f"{p['title']} — Phi Tran", p["summary"], 2, f"work/{p['slug']}/")
        + body
        + tail(2, "../../#about", "../")
    )
    out = WORK / p["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")


def reading_time(post):
    """Minutes at 200 wpm, computed from the body so it cannot drift."""
    words = sum(len(re.sub(r"<[^>]+>", " ", b).split()) for _, b in post["body"])
    return max(1, round(words / 200))


def pretty_date(iso):
    y, m, d = iso.split("-")
    return f"{d} {MONTHS[int(m) - 1]} {y}"


def build_blog_index(posts):
    rows = []
    for p in posts:
        rows.append(f"""      <a class="post rv" href="{p['slug']}/">
        <div class="post-meta">
          <span class="post-date">{pretty_date(p['date'])}</span>
          <span class="post-tag">{html.escape(p['tag'])}</span>
          <span class="post-time">{reading_time(p)} min</span>
        </div>
        <h2 class="post-title">{html.escape(p['title'])}</h2>
        <p class="post-ex">{html.escape(p['excerpt'])}</p>
        <span class="post-go">Read ↗</span>
      </a>
""")

    body = f"""
<div class="wrap">

  <div class="work-head">
    <div></div>
    <div>
      <span class="pill">Notes &amp; essays</span>
      <h1 class="work-title" data-scramble>BLOG</h1>
      <p class="detail-sum" style="margin-top:20px">
        Written when something turned out differently than expected — protocol
        internals, infrastructure decisions, and the occasional claim that did
        not survive checking.
      </p>
    </div>
  </div>

  <div class="posts">
{''.join(rows)}  </div>
</div>

<footer class="wrap">
  <p class="lab">Contact</p>
  <div class="mail-row">
    <a class="big-mail" href="mailto:phitranviet99@gmail.com">phitranviet99@gmail.com</a>
    <button class="copy" data-copy="phitranviet99@gmail.com" aria-label="Copy email address">Copy</button>
  </div>
  <div class="foot-row">
    <span><a href="../">← Back home</a></span>
    <span>
      <a href="https://github.com/philliptran1402">GitHub</a> ·
      <a href="https://linkedin.com/in/phitrantech">LinkedIn</a>
    </span>
    <span>© 2026 Phi Tran</span>
  </div>
</footer>
"""
    page = (head("Blog — Phi Tran",
                 "Notes on protocol internals, infrastructure decisions and verification.",
                 1, "blog/")
            + body + tail(1, "../#about", "../work/", "./"))
    BLOG.mkdir(exist_ok=True)
    (BLOG / "index.html").write_text(page, encoding="utf-8")


def build_post(p, prev_p, next_p):
    sections = ""
    for h, b in p["body"]:
        head_html = f'    <p class="lab">{html.escape(h)}</p>\n' if h else ""
        sections += f'\n  <section class="rv">\n{head_html}    <div class="prose">{b}</div>\n  </section>\n'

    nav = []
    nav.append(f'<a href="../{prev_p["slug"]}/">← {html.escape(prev_p["title"][:44])}</a>' if prev_p else "<span></span>")
    nav.append('<a href="../">All posts</a>')
    nav.append(f'<a href="../{next_p["slug"]}/">{html.escape(next_p["title"][:44])} →</a>' if next_p else "<span></span>")

    body = f"""
<div class="wrap">

  <div class="detail-head">
    <p class="crumb"><a href="../">Blog</a> <span>/</span> {html.escape(p['tag'])}</p>
    <div class="post-meta" style="margin-bottom:6px">
      <span class="post-date">{pretty_date(p['date'])}</span>
      <span class="post-time">{reading_time(p)} min read</span>
    </div>
    <h1 class="detail-title">{html.escape(p['title'])}</h1>
    <p class="detail-sum">{html.escape(p['excerpt'])}</p>
  </div>
{sections}
  <nav class="pager">
    {nav[0]}
    {nav[1]}
    {nav[2]}
  </nav>
</div>

<footer class="wrap">
  <p class="lab">Contact</p>
  <div class="mail-row">
    <a class="big-mail" href="mailto:phitranviet99@gmail.com">phitranviet99@gmail.com</a>
    <button class="copy" data-copy="phitranviet99@gmail.com" aria-label="Copy email address">Copy</button>
  </div>
  <div class="foot-row">
    <span><a href="../">← All posts</a></span>
    <span>
      <a href="https://github.com/philliptran1402">GitHub</a> ·
      <a href="https://linkedin.com/in/phitrantech">LinkedIn</a>
    </span>
    <span>© 2026 Phi Tran</span>
  </div>
</footer>
"""
    page = (head(f"{p['title']} — Phi Tran", p["excerpt"], 2, f"blog/{p['slug']}/")
            + body + tail(2, "../../#about", "../../work/", "../"))
    out = BLOG / p["slug"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")


def main():
    projects = json.loads(PROJECTS.read_text(encoding="utf-8"))
    by_slug = {p["slug"]: p for p in projects}

    slugs = [p["slug"] for p in projects]
    if len(set(slugs)) != len(slugs):
        sys.exit("duplicate slug in projects.json")
    for p in projects:
        if p.get("related") and p["related"] not in by_slug:
            sys.exit(f"{p['slug']}: related slug '{p['related']}' does not exist")

    WORK.mkdir(exist_ok=True)
    total, counts = build_index(projects)

    for i, p in enumerate(projects):
        build_detail(p, projects[i - 1] if i else None,
                     projects[i + 1] if i + 1 < len(projects) else None, by_slug)

    posts = json.loads(POSTS.read_text(encoding="utf-8"))
    posts.sort(key=lambda x: x["date"], reverse=True)
    pslugs = [x["slug"] for x in posts]
    if len(set(pslugs)) != len(pslugs):
        sys.exit("duplicate slug in posts.json")

    build_blog_index(posts)
    for i, p in enumerate(posts):
        build_post(p, posts[i - 1] if i else None,
                   posts[i + 1] if i + 1 < len(posts) else None)

    print(f"work/index.html  — {total} projects {counts}")
    print(f"work/<slug>/     — {len(projects)} detail pages")
    print(f"blog/index.html  — {len(posts)} posts")
    print(f"blog/<slug>/     — {len(posts)} post pages")


if __name__ == "__main__":
    main()
