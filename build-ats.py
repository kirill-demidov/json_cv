#!/usr/bin/env python3
"""Generate single-column ATS-safe CV outputs from the JSON resume.

Projects are intentionally omitted: they stay on the web version only.

Two-column HTML gets scrambled by most resume parsers. This builds two linear
artifacts: a plain-text file to paste into application forms, and cv-ats.html,
which build-pdf.sh renders into Kirill_Demidov_CV_ATS.pdf for portal uploads.
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "cv_Kirill_Demidov_DE.json"
OUT = ROOT / "Kirill_Demidov_CV_ATS.txt"
OUT_HTML = ROOT / "cv-ats.html"

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def fmt_date(value):
    if not value:
        return "Present"
    y, m, *_ = value.split("-")
    return f"{MONTHS[int(m)]} {y}"


def rule(char="="):
    return char * 72


def section(title):
    return f"\n{title.upper()}\n{rule('-')}"


def main():
    cv = json.loads(SRC.read_text())
    b = cv["basics"]
    out = []

    out.append(b["name"].upper())
    out.append(b["label"])
    contacts = [b["email"], b["phone"], b["location"]["address"]]
    contacts += [p["url"].replace("https://www.", "").replace("https://", "").rstrip("/")
                 for p in b.get("profiles", [])]
    out.append(" | ".join(contacts))
    out.append(rule())
    out.append("")
    out.append(b["summary"])

    out.append(section("Experience"))
    for w in cv["work"]:
        out.append("")
        out.append(f"{w['position']}")
        out.append(f"{w['name']} | {w.get('location', '')}")
        out.append(f"{fmt_date(w['startDate'])} - {fmt_date(w.get('endDate'))}")
        if w.get("summary"):
            out.append(w["summary"])
        for h in w.get("highlights", []):
            out.append(f"- {h}")

    out.append(section("Skills"))
    for s in cv["skills"]:
        out.append(f"{s['name']}: {', '.join(s['keywords'])}")

    if cv.get("publications"):
        out.append(section("Publications"))
        for p in cv["publications"]:
            out.append(f"- {p['name']} — {p.get('publisher', '')}, "
                       f"{p.get('releaseDate', '')[:4]}. {p.get('url', '')}")

    if cv.get("awards"):
        out.append(section("Patents & Awards"))
        for a in cv["awards"]:
            out.append(f"- {a['title']} — {a.get('awarder', '')}, "
                       f"{a.get('date', '')[:4]}.")

    out.append(section("Education & Certifications"))
    for e in cv["education"]:
        line = f"- {e.get('studyType', '')} {e.get('area', '')}".strip()
        out.append(f"{line}, {e.get('institution', '')} "
                   f"({e.get('startDate', '')[:4]}-{e.get('endDate', '')[:4]})")

    if cv.get("languages"):
        out.append(section("Languages"))
        out.append(", ".join(f"{l['language']} ({l['fluency']})" for l in cv["languages"]))

    out.append("")
    out.append(f"Generated {date.today().isoformat()} from cv_Kirill_Demidov_DE.json")

    OUT.write_text("\n".join(out) + "\n")
    print(f"{OUT.name} written ({len(out)} lines)")

    OUT_HTML.write_text(render_html(cv))
    print(f"{OUT_HTML.name} written")


def render_html(cv):
    """Single-column, tag-free markup: headings, paragraphs and lists only."""
    e = html.escape
    b = cv["basics"]
    p = []

    contacts = [b["email"], b["phone"], b["location"]["address"]]
    contacts += [pr["url"].replace("https://www.", "").replace("https://", "").rstrip("/")
                 for pr in b.get("profiles", [])]

    p.append(f"<h1>{e(b['name'])}</h1>")
    p.append(f"<p class='label'>{e(b['label'])}</p>")
    p.append(f"<p class='contacts'>{e(' | '.join(contacts))}</p>")
    p.append(f"<p class='summary'>{e(b['summary'])}</p>")

    p.append("<h2>Experience</h2>")
    for w in cv["work"]:
        p.append("<div class='entry'>")
        p.append(f"<h3>{e(w['position'])}</h3>")
        p.append(f"<p class='meta'>{e(w['name'])}"
                 f"{' | ' + e(w['location']) if w.get('location') else ''} | "
                 f"{fmt_date(w['startDate'])} - {fmt_date(w.get('endDate'))}</p>")
        if w.get("summary"):
            p.append(f"<p>{e(w['summary'])}</p>")
        if w.get("highlights"):
            p.append("<ul>" + "".join(f"<li>{e(h)}</li>" for h in w["highlights"]) + "</ul>")
        p.append("</div>")

    p.append("<h2>Skills</h2>")
    for s in cv["skills"]:
        p.append(f"<p><strong>{e(s['name'])}:</strong> {e(', '.join(s['keywords']))}</p>")

    if cv.get("publications"):
        p.append("<h2>Publications</h2><ul>")
        for pub in cv["publications"]:
            p.append(f"<li>{e(pub['name'])} — {e(pub.get('publisher', ''))}, "
                     f"{e(pub.get('releaseDate', '')[:4])}. {e(pub.get('url', ''))}</li>")
        p.append("</ul>")

    if cv.get("awards"):
        p.append("<h2>Patents &amp; Awards</h2><ul>")
        for a in cv["awards"]:
            p.append(f"<li>{e(a['title'])} — {e(a.get('awarder', ''))}, "
                     f"{e(a.get('date', '')[:4])}.</li>")
        p.append("</ul>")

    p.append("<h2>Education &amp; Certifications</h2><ul>")
    for ed in cv["education"]:
        line = f"{ed.get('studyType', '')} {ed.get('area', '')}".strip()
        p.append(f"<li>{e(line)}, {e(ed.get('institution', ''))} "
                 f"({e(ed.get('startDate', '')[:4])}-{e(ed.get('endDate', '')[:4])})</li>")
    p.append("</ul>")

    if cv.get("languages"):
        p.append("<h2>Languages</h2>")
        p.append("<p>" + e(", ".join(f"{l['language']} ({l['fluency']})"
                                     for l in cv["languages"])) + "</p>")

    body = "\n".join(p)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{e(b['name'])} — {e(b['label'])}</title>
<style>
  /* ATS-safe: one column, no floats, no grid, no background graphics */
  @page {{ size: A4; margin: 11mm 12mm; }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9.2pt;
    line-height: 1.25;
    color: #000;
    background: #fff;
    max-width: 190mm;
    margin: 0 auto;
    padding: 0;
  }}
  h1 {{ font-size: 15pt; margin: 0 0 2pt; }}
  .label {{ font-size: 10pt; margin: 0 0 3pt; }}
  .contacts {{ font-size: 8.8pt; margin: 0 0 7pt; }}
  .summary {{ margin: 0 0 8pt; }}
  h2 {{
    font-size: 10.5pt;
    margin: 9pt 0 4pt;
    padding-bottom: 2pt;
    border-bottom: 1px solid #000;
    text-transform: uppercase;
  }}
  h3 {{ font-size: 9.8pt; margin: 0 0 1pt; }}
  .meta {{ font-size: 8.8pt; margin: 0 0 2pt; }}
  .entry {{ margin-bottom: 6pt; page-break-inside: avoid; }}
  p {{ margin: 0 0 3pt; }}
  ul {{ margin: 3pt 0 0; padding-left: 16pt; }}
  li {{ margin-bottom: 1pt; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


if __name__ == "__main__":
    main()
