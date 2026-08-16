#!/usr/bin/env python3
"""Собирает index.html из cv_Kirill_Demidov_DE.json.

Раньше вёрстка была написанной руками копией JSON, и данные в двух файлах
расходились: имя компании пришлось править в обоих, набор навыков в вёрстке
успел обогнать JSON, а из проектов часть не попала в резюме вовсе.

Генерация идёт при сборке, не в браузере: CV должно читаться Гуглом и превью
LinkedIn, а не требовать JS. Запуск: python3 build.py [--check]
  --check  ничего не пишет, только сообщает, что index.html разошёлся с JSON
"""

import html
import json
import re
import sys
from datetime import date

CV = "cv_Kirill_Demidov_DE.json"
OUT = "index.html"
PDF = "Kirill_Demidov_CV.pdf"
PDF_ATS = "Kirill_Demidov_CV_ATS.pdf"
TXT_ATS = "Kirill_Demidov_CV_ATS.txt"
RECENT = 3          # столько последних позиций показываем раскрытыми
COLLAPSED_HL = 1    # у свёрнутых — по одному пункту, иначе блок разрастается

MONTHS = ("January February March April May June July August September "
          "October November December").split()


def e(s):
    return html.escape(str(s or ""))


def month_year(iso):
    """2024-07-01 -> July 2024"""
    if not iso:
        return "Present"
    y, m = int(iso[:4]), int(iso[5:7])
    return f"{MONTHS[m - 1]} {y}"


def year(iso):
    return iso[:4] if iso else "Present"


def phone(raw):
    """+972542332917 -> +972 54 233 2917"""
    m = re.fullmatch(r"\+(\d{3})(\d{2})(\d{3})(\d{4})", raw or "")
    return f"+{m[1]} {m[2]} {m[3]} {m[4]}" if m else raw


def initials(name):
    return "".join(w[0] for w in name.split()[:2]).upper()


def tags(items):
    return "\n              ".join(f'<span class="tag">{e(i)}</span>' for i in items)


def highlights(items, indent=14):
    pad = " " * indent
    inner = "".join(f"\n{pad}  <li>{e(h)}</li>" for h in items)
    return f'{pad}<ul class="highlights">{inner}\n{pad}</ul>' if items else ""


def experience_item(w, collapsed):
    """Одна позиция. Свёрнутые идут короче: годы, краткие подписи, один пункт."""
    pos = w.get("displayPosition") if collapsed else None
    pos = pos or w["position"]
    name = (w.get("displayName") if collapsed else None) or w["name"]
    if collapsed:
        when = f'{year(w.get("startDate"))} – {year(w.get("endDate"))}'
        company = f'<span class="company-name">{e(name)}</span>'
        # displayHighlight — отдельная выжимка для свёрнутого вида; она обычно
        # написана лучше, чем первый пункт полного списка
        one = w.get("displayHighlight")
        hl = highlights([one] if one else w.get("highlights", [])[:COLLAPSED_HL], 16)
        summary = ""
        pad = "            "
    else:
        when = (f'{month_year(w.get("startDate"))} – {month_year(w.get("endDate"))}'
                ' <span class="duration"></span>')
        url = w.get("url")
        company = (f'<a href="{e(url)}" class="company-name">{e(name)}</a>' if url
                   else f'<span class="company-name">{e(name)}</span>')
        hl = highlights(w.get("highlights", []), 14)
        summary = f'\n            <p class="summary">{e(w.get("summary"))}</p>' if w.get("summary") else ""
        pad = "          "
    lines = [
        f'{pad}<div class="experience-item">',
        f'{pad}  <div class="item-header">',
        f'{pad}    <h3>{e(pos)}</h3>',
        f'{pad}    <span class="date-range" data-start="{e(w.get("startDate"))}"'
        f' data-end="{e(w.get("endDate") or "Present")}">{when}</span>',
        f'{pad}  </div>',
        f'{pad}  {company}{summary}',
    ]
    if hl:
        lines.append(hl)
    lines.append(f'{pad}</div>')
    return "\n".join(lines)


def project_item(p):
    entity = e(p.get("entity") or "")
    if p.get("url"):
        label = p["url"].replace("https://github.com/", "").replace("https://", "")
        link = f'<a href="{e(p["url"])}">{e(label)}</a>'
        entity = f"{entity} | {link}" if entity else link
    when = year(p.get("startDate"))
    end = p.get("endDate")
    when = f"{when} – {year(end)}" if end and year(end) != when else (
        f"{when} – Present" if not end else when)
    return (f'          <div class="project-item">\n'
            f'            <div class="item-header">\n'
            f'              <h3>{e(p["name"])}</h3>\n'
            f'              <span class="date-range">{when}</span>\n'
            f'            </div>\n'
            f'            <div class="project-entity">{entity}</div>\n'
            f'            <p class="summary">{e(p.get("description"))}</p>\n'
            f'{highlights(p.get("highlights", [])[:3])}\n'
            f'          </div>')


def render(d):
    b = d["basics"]
    by_net = {p["network"]: p for p in b.get("profiles", [])}

    # текстовые лейблы вместо эмодзи: часть PDF-парсеров рисует их кракозябрами,
    # а сам адрес виден и на распечатке, где по ссылке не кликнешь
    def row(label, value):
        return f'<li><span class="contact-label">{label}</span> {value}</li>'

    contact = [row("Email", f'<a href="mailto:{e(b["email"])}">{e(b["email"])}</a>')]
    if b.get("phone"):
        contact.append(row("Phone", f'<a href="tel:{e(b["phone"])}">{e(phone(b["phone"]))}</a>'))
    contact.append(row("Location", e(b["location"]["address"])))
    for net in ("LinkedIn", "GitHub"):
        if net in by_net:
            url = by_net[net]["url"]
            shown = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
            contact.append(row(net, f'<a href="{e(url)}">{e(shown)}</a>'))

    skills = "\n".join(
        f'          <div class="skill-category">\n'
        f'            <h4>{e(s["name"])}</h4>\n'
        f'            <div class="skill-tags">\n'
        f'              {tags(s.get("keywords", []))}\n'
        f'            </div>\n'
        f'          </div>' for s in d.get("skills", []))

    work = sorted(d["work"], key=lambda w: w.get("startDate") or "", reverse=True)
    recent = "\n\n".join(experience_item(w, False) for w in work[:RECENT])
    older = "\n".join(experience_item(w, True) for w in work[RECENT:])
    older_years = (f'{year(work[-1].get("startDate"))} – '
                   f'{year(work[RECENT].get("endDate"))}') if work[RECENT:] else ""

    projects = "\n\n".join(project_item(p) for p in d.get("projects", []))

    pubs = []
    for a in d.get("awards", []):
        # в заголовок — номер («US Patent 10,838,836»), под него описательное
        # название из title: одно ищут глазами, другое объясняет, о чём патент
        num = re.search(r"US ?([\d,]+)", a.get("awarder", ""))
        head = f'US Patent {num[1]}' if num else a["title"]
        if a.get("url"):
            head = f'<a href="{e(a["url"])}">{e(head)}</a>'
        else:
            head = e(head)
        awarder = re.sub(r"\s*\(.*\)$", "", a.get("awarder", ""))
        desc = re.sub(r"^Patent:\s*", "", a.get("title", ""))
        pubs.append(
            f'          <div class="project-item">\n'
            f'            <div class="item-header">\n'
            f'              <h3>{head}</h3>\n'
            f'              <span class="date-range">{year(a.get("date"))}</span>\n'
            f'            </div>\n'
            f'            <div class="project-entity">{e(awarder)}</div>\n'
            f'            <p class="summary">{e(desc)}. {e(a.get("summary"))}</p>\n'
            f'          </div>')
    for p in d.get("publications", []):
        pubs.append(
            f'          <div class="project-item">\n'
            f'            <div class="item-header">\n'
            f'              <h3><a href="{e(p.get("url"))}">{e(p["name"])}</a></h3>\n'
            f'              <span class="date-range">{year(p.get("releaseDate"))}</span>\n'
            f'            </div>\n'
            f'            <div class="project-entity">{e(p.get("publisher"))}</div>\n'
            f'            <p class="summary">{e(p.get("summary"))}</p>\n'
            f'          </div>')

    degrees, certs = [], []
    for ed in d.get("education", []):
        if (ed.get("studyType") or "").lower() in ("master", "bachelor", "phd"):
            degrees.append(
                f'        <div class="education-item">\n'
                f'          <div class="item-header">\n'
                f'            <h3>{e(ed["institution"])}</h3>\n'
                f'            <span class="date-range">{year(ed.get("startDate"))} – '
                f'{year(ed.get("endDate"))}</span>\n'
                f'          </div>\n'
                f'          <p>{e(ed.get("studyType"))} of {e(ed.get("area"))}</p>\n'
                f'        </div>')
        else:
            # в скобках и тип, и кто выдал: в прежней вёрстке было то одно,
            # то другое, и половина сертификатов выглядела безымянной
            name = e(ed.get("area") or ed.get("institution"))
            if ed.get("url"):
                name = f'<a href="{e(ed["url"])}">{name}</a>'
            paren = ", ".join(x for x in (ed.get("studyType"), ed.get("institution")) if x)
            certs.append(f'            <li><strong>{name}</strong> ({e(paren)})</li>')
    if certs:
        degrees.append('        <div class="education-item">\n'
                       '          <div class="item-header">\n'
                       '            <h3>Professional Certifications</h3>\n'
                       '          </div>\n'
                       '          <ul class="highlights">\n'
                       + "\n".join(certs) +
                       '\n          </ul>\n'
                       '        </div>')

    langs = tags(f'{l["language"]} ({l["fluency"].replace(" speaker", "")})'
                 for l in d.get("languages", []))

    older_block = (f'''
        <details id="early-career" class="early-career">
          <summary>View work experience ({older_years})</summary>
          <h3 class="early-career-title">Earlier experience ({older_years})</h3>
          <div class="experience-list">
{older}
          </div>
        </details>''' if older else "")

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(b["name"])} | {e(b["label"])}</title>
  <meta name="description" content="{e(b.get("summary"))}">
  <!-- Собрано из {CV} скриптом build.py — руками не править. -->
  <link rel="stylesheet" href="index.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="container">
    <aside>
      <div class="profile-img">{e(initials(b["name"]))}</div>
      <header>
        <h1>{e(b["name"])}</h1>
        <div class="label">{e(b["label"])}</div>
        <p class="summary-text" style="font-size: 0.9rem; margin-bottom: 2rem; color: var(--text-muted);">
          {e(b.get("summary"))}
        </p>
      </header>

      <section id="contact">
        <h2>Contact</h2>
        <ul class="contact-info">
          {chr(10).join("  " + c for c in contact).strip()}
        </ul>
        <div class="downloads">
          <a class="download-btn" href="{PDF}" download>⬇︎ Download PDF</a>
          <a class="download-link" href="{PDF_ATS}" download>ATS PDF</a>
          <a class="download-link" href="{TXT_ATS}" download>TXT</a>
          <a class="download-link" href="{CV}" download>JSON</a>
        </div>
      </section>

      <section id="skills-overview">
        <h2>Core Expertise</h2>
        <div class="skills-stack" style="display: flex; flex-direction: column; gap: 1.25rem;">
{skills}
        </div>
      </section>
    </aside>

    <main>
      <section id="work">
        <h2>Experience</h2>
        <div class="experience-list">
{recent}
        </div>
{older_block}
      </section>

      <section id="projects">
        <h2>Key Projects</h2>
        <div class="project-list">
{projects}
        </div>
      </section>

      <section id="publications">
        <h2>Publications &amp; Patents</h2>
        <div class="project-list">
{chr(10).join(pubs)}
        </div>
      </section>

      <section id="education">
        <h2>Education &amp; Certifications</h2>
{chr(10).join(degrees)}
      </section>

      <section id="languages">
        <h2>Languages</h2>
        <div class="skill-tags">
          {langs}
        </div>
      </section>
    </main>
  </div>

  <script>
    // «· 2 yrs 1 mo» рядом с датами — считаем в браузере, чтобы длительность
    // текущей работы не устаревала со дня сборки
    function calculateDuration(startStr, endStr) {{
      const start = new Date(startStr);
      const end = endStr === 'Present' ? new Date() : new Date(endStr);
      let years = end.getFullYear() - start.getFullYear();
      let months = end.getMonth() - start.getMonth();
      if (months < 0) {{ years--; months += 12; }}
      const res = [];
      if (years > 0) res.push(`${{years}} yr${{years > 1 ? 's' : ''}}`);
      if (months > 0) res.push(`${{months}} mo${{months > 1 ? 's' : ''}}`);
      return res.length ? `· ${{res.join(' ')}}` : '';
    }}

    document.querySelectorAll('.date-range').forEach(el => {{
      const start = el.getAttribute('data-start');
      const end = el.getAttribute('data-end');
      const durationEl = el.querySelector('.duration');
      if (start && end && durationEl) durationEl.textContent = calculateDuration(start, end);
    }});

    // в PDF свёрнутый аккордеон читается как дыра в хронологии, а стрелка — как баг
    const earlyCareer = document.getElementById('early-career');
    if (earlyCareer) {{
      if (window.matchMedia('print').matches) earlyCareer.open = true;
      window.addEventListener('beforeprint', () => {{ earlyCareer.open = true; }});
    }}
  </script>
</body>
</html>
'''


def main():
    with open(CV) as f:
        d = json.load(f)
    out = render(d)
    if "--check" in sys.argv:
        try:
            with open(OUT) as f:
                current = f.read()
        except OSError:
            current = ""
        if current != out:
            print(f"{OUT} разошёлся с {CV}: запусти python3 build.py", file=sys.stderr)
            return 1
        print(f"{OUT} соответствует {CV}")
        return 0
    with open(OUT, "w") as f:
        f.write(out)
    print(f"{OUT}: {len(out)} байт, {len(d['work'])} позиций, "
          f"{len(d.get('projects', []))} проектов")
    return 0


if __name__ == "__main__":
    sys.exit(main())
