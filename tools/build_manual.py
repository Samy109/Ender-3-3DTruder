"""
Build Ender_3_3DTruder_Master_Manual.html (and .pdf) from ender_3_3dtruder_master_manual.md.

    pip install markdown
    python tools/build_manual.py          # HTML + PDF (PDF needs Microsoft Edge or Chrome)
    python tools/build_manual.py --html   # HTML only

The markdown file is the source of truth; never hand-edit the HTML or PDF.
"""
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "ender_3_3dtruder_master_manual.md"
HTML_OUT = ROOT / "Ender_3_3DTruder_Master_Manual.html"
PDF_OUT = ROOT / "Ender_3_3DTruder_Master_Manual.pdf"
CSS = (Path(__file__).parent / "manual.css").read_text(encoding="utf-8")
REVISION = "4.0"

CALLOUTS = {"CAUTION": ("danger", "&times;"), "WARNING": ("warning", "!"),
            "IMPORTANT": ("warning", "!"), "NOTE": ("info", "&#9432;"), "TIP": ("success", "&check;")}

COVER = f"""
<div class="cover-page">
  <div class="cover-header">
    <div class="brand-badge">Build &amp; Operating Manual</div>
    <div class="cover-title">3DTRUDER MASTER MANUAL</div>
    <div class="cover-subtitle">Auger-Fed Super Volcano Extrusion Line</div>
    <div class="cover-desc">Turns an Ender 3 V2 into a closed-loop recycling line that extrudes shredded plastic into 1.75 mm filament.</div>
  </div>
  <div class="cover-grid">
    <div class="spec-card"><div class="spec-card-title">Melt Path</div>
      <div class="spec-card-val">Brass Coupler &rarr; Super Volcano</div>
      <div style="font-size:8pt;color:#64748b;margin-top:2px;">Two heat zones: 80 W block + 40 W heated coupler, no heatbreak</div></div>
    <div class="spec-card"><div class="spec-card-title">Nozzle</div>
      <div class="spec-card-val">1.4 mm Brass Super Volcano</div>
      <div style="font-size:8pt;color:#64748b;margin-top:2px;">Die swell drawn down to 1.75 mm by the puller</div></div>
    <div class="spec-card"><div class="spec-card-title">Auger Drive</div>
      <div class="spec-card-val">14:1 NEMA 17 + 51100 Bearing</div>
      <div style="font-size:8pt;color:#64748b;margin-top:2px;">3/8" auger in a 10 &times; 12 mm stainless barrel, ~0.7 A torque limit</div></div>
    <div class="spec-card"><div class="spec-card-title">Control</div>
      <div class="spec-card-val">Arduino V4 + Marlin Soak Timer</div>
      <div style="font-size:8pt;color:#64748b;margin-top:2px;">Interrupt-driven motors, dead-time-aware diameter loop</div></div>
  </div>
  <div class="cover-footer">
    <div><strong>Revision:</strong> {REVISION} ({date.today():%B %Y})</div>
    <div><strong>Platform:</strong> Ender 3 V2 Conversion</div>
    <div><strong>Output:</strong> 1.75 mm Recycled Filament</div>
  </div>
</div>
"""


def convert_callouts(md_text: str) -> str:
    """Turn GitHub '> [!NOTE]' blockquotes into styled callout divs."""
    out, lines, i = [], md_text.splitlines(), 0
    while i < len(lines):
        m = re.match(r"^>\s*\[!(\w+)\]\s*$", lines[i])
        if m and m.group(1) in CALLOUTS:
            kind, icon = CALLOUTS[m.group(1)]
            body = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(lines[i][1:].lstrip())
                i += 1
            inner = markdown.markdown("\n".join(body), extensions=["tables"])
            out.append(f'<div class="callout callout-{kind}"><div class="callout-title">{icon} '
                       f'{m.group(1).title()}</div>{inner}</div>')
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def build_html() -> str:
    md_text = SRC.read_text(encoding="utf-8")
    md_text = re.sub(r"\A# .*\n(\*\*.*\*\*\n)?", "", md_text)   # title lives on the cover page
    body = markdown.markdown(convert_callouts(md_text), extensions=["tables", "fenced_code"])

    # Markdown "##" sections become page-level h1, "###" become h2 (matches the stylesheet)
    body = re.sub(r"<(/?)h3>", r"<\1h2_>", body)
    body = re.sub(r"<(/?)h2>", r"<\1h1>", body)
    body = body.replace("<h2_>", "<h2>").replace("</h2_>", "</h2>")
    body = body.replace("<hr />", "")

    # Each section starts on a new page with a running header
    parts = re.split(r"(?=<h1>)", body)
    pages = []
    for n, part in enumerate(p for p in parts if p.strip()):
        title = re.sub("<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", part).group(1)) if "<h1>" in part else ""
        title = re.sub(r"^[^\w\d]+", "", title).strip()
        brk = '<div class="page-break"></div>' if n else ""
        pages.append(f'{brk}<div class="header-rule"><span>3DTruder Master Manual</span>'
                     f"<span>{title}</span></div>\n{part}")

    return (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>3DTruder Master Manual</title>\n<style>\n{CSS}\n"
            "pre code { background: none; border: none; padding: 0; color: inherit; font-size: inherit; }\n"
            f"</style>\n</head>\n<body>\n{COVER}\n{''.join(pages)}\n</body>\n</html>\n")


def find_browser():
    for c in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
        if Path(c).exists():
            return c
    return shutil.which("msedge") or shutil.which("google-chrome") or shutil.which("chromium")


def main():
    HTML_OUT.write_text(build_html(), encoding="utf-8", newline="\n")
    print("wrote", HTML_OUT.name)
    if "--html" in sys.argv:
        return
    browser = find_browser()
    if not browser:
        sys.exit("No Edge/Chrome found; PDF not built.")
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF_OUT}", HTML_OUT.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    print("wrote", PDF_OUT.name)


if __name__ == "__main__":
    main()
