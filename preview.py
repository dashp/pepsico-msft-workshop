"""Local preview server for the PepsiCo workshop site.

Renders Markdown files in this folder tree to HTML with a Cayman-like
theme so you can browse the workshop content before the real Jekyll
site is published to GitHub Pages.

Usage:
    pip install markdown pygments
    python preview.py
    # then open http://localhost:4000/

This is a preview only. The published site is built by Jekyll on
GitHub Pages from the same .md files.
"""
from __future__ import annotations

import http.server
import os
import pathlib
import re
import socketserver
import urllib.parse

import markdown

ROOT = pathlib.Path(__file__).parent.resolve()
PORT = 4000
SITE_TITLE = "PepsiCo \u00d7 Microsoft \u2014 Data & AI Workshop (Day 1)"

MD_EXTS = [
    "fenced_code", "tables", "toc", "sane_lists", "attr_list",
    "codehilite", "md_in_html",
]
MD_EXT_CFG = {"codehilite": {"guess_lang": False, "css_class": "highlight"}}

# Files that should appear in the left-nav, in order.
NAV = [
    ("Home", "index.md"),
    ("\u2014 Labs \u2014", None),
    ("Lab 01 \u2014 Fabric Lakehouse + Data Agent",
     "Instructions/Labs/LAB_01-Fabric_Lakehouse_Data_Agent.md"),
    ("Lab 02 \u2014 Real-Time Intelligence",
     "Instructions/Labs/LAB_02-Real_Time_Intelligence.md"),
    ("Lab 03 \u2014 Vector Search on Azure SQL",
     "Instructions/Labs/LAB_03-Vector_Search_Azure_SQL.md"),
    ("Lab 04 \u2014 Azure ML Agent Tool",
     "Instructions/Labs/LAB_04-Azure_ML_Agent_Tool.md"),
    ("\u2014 Demos \u2014", None),
    ("Demo 00 \u2014 Pre-flight (instructor)",
     "Instructions/Demos/DEMO_00-Pre_flight.md"),
    ("Demo 01 \u2014 Purview + Fabric IQ",
     "Instructions/Demos/DEMO_01-Purview_Fabric_IQ.md"),
    ("\u2014 Reference \u2014", None),
    ("README", "README.md"),
]

CSS = """
:root { --accent:#159957; --accent2:#155799; --fg:#2b2b2b; --muted:#606c71;
        --bg:#fff; --code:#f3f6fa; --border:#e6e6e6; }
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI",
       Helvetica, Arial, sans-serif; color: var(--fg); background: var(--bg); }
.header { background: linear-gradient(120deg, var(--accent2), var(--accent));
          color: #fff; padding: 1.6rem 2rem; }
.header h1 { margin: 0; font-size: 1.5rem; font-weight: 600; }
.header a { color: rgba(255,255,255,.85); text-decoration: none; }
.layout { display: flex; min-height: calc(100vh - 84px); }
.sidebar { width: 320px; flex: 0 0 320px; border-right: 1px solid var(--border);
           padding: 1.5rem 1rem 2rem 1.5rem; background: #fafbfc; overflow-y: auto; }
.sidebar h3 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em;
              color: var(--muted); margin: 1.2rem 0 0.4rem; font-weight: 600; }
.sidebar ul { list-style: none; padding: 0; margin: 0; }
.sidebar li { margin: 0.2rem 0; }
.sidebar a { color: var(--fg); text-decoration: none; display: block;
             padding: 0.3rem 0.5rem; border-radius: 4px; font-size: 0.95rem; }
.sidebar a:hover { background: #eaeef2; }
.sidebar a.active { background: var(--accent); color: #fff; }
.content { flex: 1; padding: 2rem 2.5rem 4rem; max-width: 900px;
           overflow-x: auto; }
.content h1 { border-bottom: 1px solid var(--border); padding-bottom: .5rem; }
.content h2 { margin-top: 2.2rem; }
.content h2, .content h3 { color: var(--accent2); }
.content table { border-collapse: collapse; margin: 1rem 0; width: 100%; }
.content th, .content td { border: 1px solid var(--border);
                           padding: 0.5rem 0.8rem; text-align: left;
                           vertical-align: top; }
.content th { background: #f3f6fa; }
.content code { background: var(--code); padding: 1px 6px; border-radius: 3px;
                font-family: SFMono-Regular, Menlo, Consolas, monospace;
                font-size: 0.9em; }
.content pre { background: var(--code); padding: 1rem; border-radius: 6px;
               overflow-x: auto; border: 1px solid var(--border); }
.content pre code { background: transparent; padding: 0; font-size: 0.88em; }
.content blockquote { border-left: 4px solid var(--accent);
                      background: #f6fdfa; margin: 1rem 0;
                      padding: 0.5rem 1rem; color: #2c3e44; }
.content img { max-width: 100%; border: 1px dashed #d0d7de; background: #fafbfc;
               padding: 1rem; border-radius: 4px; color: #888; }
.content a { color: var(--accent2); }
.banner { background: #fff8e1; border: 1px solid #f1c40f; padding: 0.75rem 1rem;
          border-radius: 4px; margin: 0 0 1.5rem; font-size: 0.92em; color: #5b4a00; }
/* codehilite */
.highlight .k, .highlight .kd, .highlight .kn { color: #d73a49; }
.highlight .s, .highlight .s1, .highlight .s2 { color: #032f62; }
.highlight .nf, .highlight .nb { color: #6f42c1; }
.highlight .c, .highlight .c1, .highlight .cm { color: #6a737d; font-style: italic; }
.highlight .nv, .highlight .vi { color: #005cc5; }
.highlight .mi, .highlight .mf { color: #005cc5; }
"""

PAGE_TPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<header class="header">
  <h1><a href="/">{site}</a></h1>
</header>
<div class="layout">
  <nav class="sidebar">{nav}</nav>
  <main class="content">
    <div class="banner">Local preview \u2014 visuals are approximate. The published GitHub Pages site uses the Cayman Jekyll theme.</div>
    {body}
  </main>
</div>
</body>
</html>
"""


def _path_to_url(rel: str) -> str:
    """Turn a relative .md path into a URL the server serves."""
    return "/" + rel.replace("\\", "/").rsplit(".", 1)[0] + ".html"


def _render_nav(active_rel: str | None) -> str:
    out = ["<ul>"]
    for label, rel in NAV:
        if rel is None:
            out.append(f"<h3>{label}</h3><ul>")
            continue
        url = _path_to_url(rel)
        cls = ' class="active"' if rel == active_rel else ""
        out.append(f'<li><a href="{url}"{cls}>{label}</a></li>')
    out.append("</ul>")
    return "\n".join(out)


def _rewrite_md_links(html: str, md_path: pathlib.Path) -> str:
    """Rewrite relative .md links so the preview can navigate between pages."""
    md_dir = md_path.parent

    def repl(m: re.Match) -> str:
        prefix, href = m.group(1), m.group(2)
        if href.startswith(("http://", "https://", "#", "mailto:", "/")):
            return f'{prefix}"{href}"'
        # split anchor
        if "#" in href:
            file_part, anchor = href.split("#", 1)
            anchor = "#" + anchor
        else:
            file_part, anchor = href, ""
        if not file_part.endswith(".md"):
            return f'{prefix}"{href}"'
        target = (md_dir / file_part).resolve()
        try:
            rel = target.relative_to(ROOT).as_posix()
        except ValueError:
            return f'{prefix}"{href}"'
        return f'{prefix}"/{rel.rsplit(".", 1)[0]}.html{anchor}"'

    return re.sub(r'(href=)"([^"]+)"', repl, html)


def render_page(md_path: pathlib.Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=MD_EXTS, extension_configs=MD_EXT_CFG)
    rel = md_path.relative_to(ROOT).as_posix()
    body = _rewrite_md_links(body, md_path)
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", body)
    page_title = re.sub(r"<[^>]+>", "", title_match.group(1)) if title_match else rel
    return PAGE_TPL.format(
        title=f"{page_title} \u2014 {SITE_TITLE}",
        site=SITE_TITLE,
        css=CSS,
        nav=_render_nav(rel),
        body=body,
    )


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quieter logs
        print("  " + fmt % args)

    def do_GET(self) -> None:  # noqa: N802
        url = urllib.parse.urlparse(self.path).path.lstrip("/")
        if url in ("", "index.html"):
            md = ROOT / "index.md"
        elif url.endswith(".html"):
            md = ROOT / (url[:-5] + ".md")
        else:
            file = ROOT / url
            if file.is_file():
                self.send_response(200)
                ext = file.suffix.lower()
                mime = {
                    ".png": "image/png", ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg", ".gif": "image/gif",
                    ".svg": "image/svg+xml", ".css": "text/css",
                    ".js": "application/javascript",
                    ".json": "application/json",
                }.get(ext, "application/octet-stream")
                self.send_header("Content-Type", mime)
                self.end_headers()
                self.wfile.write(file.read_bytes())
                return
            self.send_error(404, f"Not found: {url}")
            return

        if not md.is_file():
            self.send_error(404, f"No such markdown: {md.name}")
            return
        html = render_page(md)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


def main() -> None:
    os.chdir(ROOT)
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as srv:
        print(f"\nPepsiCo workshop preview at http://localhost:{PORT}/\n")
        print("Press Ctrl+C to stop.\n")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
