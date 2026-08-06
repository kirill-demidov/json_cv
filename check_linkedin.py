#!/usr/bin/env python3
"""Сверяет CV с выгрузкой LinkedIn и печатает расхождения.

Двусторонней синхронизации не существует: писать в профиль LinkedIn нечем —
API для этого нет, а автоматизация браузером нарушает их соглашение. Читать
профиль целиком тоже нечем. Единственный законный путь — официальная выгрузка:
Settings -> Data privacy -> Get a copy of your data.

Поэтому здесь не синхронизация, а сторож: он показывает, что разъехалось, а
правки ты вносишь сам — в JSON или в профиле.

    python3 check_linkedin.py ~/Downloads/Basic_LinkedInDataExport_*.zip
    python3 check_linkedin.py путь/к/распакованной/папке

Выгрузка содержит и личное — контакты, переписку, телефоны. Скрипт читает
только профильные файлы и ничего не сохраняет; сам архив в репозиторий не кладём.
"""

import csv
import io
import json
import os
import re
import sys
import zipfile

CV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "cv_Kirill_Demidov_DE.json")
# читаем только это; Connections, messages, PhoneNumbers и прочее не трогаем
WANTED = ("Profile.csv", "Positions.csv", "Projects.csv",
          "Publications.csv", "Skills.csv", "Languages.csv")


def load_export(path):
    """{имя файла: [строки]} из zip или распакованной папки."""
    out = {}
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                base = os.path.basename(name)
                if base in WANTED:
                    with z.open(name) as f:
                        text = io.TextIOWrapper(f, encoding="utf-8-sig")
                        out[base] = list(csv.DictReader(text))
    else:
        for base in WANTED:
            p = os.path.join(path, base)
            if os.path.isfile(p):
                with open(p, encoding="utf-8-sig") as f:
                    out[base] = list(csv.DictReader(f))
    return out


def norm(s):
    """Для сравнения имён: регистр, пробелы и знаки не считаются."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def report(title, lines):
    if lines:
        print(f"\n{title}")
        for l in lines:
            print(f"  {l}")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    ex = load_export(argv[0])
    if not ex:
        print(f"в {argv[0]} не нашлось профильных файлов выгрузки", file=sys.stderr)
        return 1
    with open(CV) as f:
        cv = json.load(f)

    problems = 0

    # --- то, что чинится только в LinkedIn ---
    li_issues = []
    for r in ex.get("Languages.csv", []):
        name = r.get("Name", "")
        if name not in {l["language"] for l in cv.get("languages", [])}:
            li_issues.append(f'язык "{name}" — в CV такого нет '
                             f'(возможно опечатка)')
    for r in ex.get("Projects.csv", []):
        t = r.get("Title", "")
        if t != t.strip():
            li_issues.append(f'проект "{t}" — лишний пробел в названии')
        if not (r.get("Url") or "").strip():
            li_issues.append(f'проект "{t.strip()}" — не заполнена ссылка')
    for r in ex.get("Publications.csv", []):
        if not (r.get("Description") or "").strip():
            li_issues.append(f'публикация "{r.get("Name","")[:40]}…" — нет описания')
    # одинаковые должность и компания с пересекающимися датами
    seen = {}
    for r in ex.get("Positions.csv", []):
        key = (norm(r.get("Title")), norm(r.get("Company Name")))
        if key in seen:
            li_issues.append(f'позиция "{r.get("Title")}" в "{r.get("Company Name")}" '
                             f'встречается дважды — похоже на дубль')
        seen[key] = r
    report("ПРАВИТЬ В LINKEDIN:", li_issues)
    problems += len(li_issues)

    # --- проекты: чего нет на той или другой стороне ---
    cv_names = {norm(p["name"]): p["name"] for p in cv.get("projects", [])}
    li_names = {norm(r["Title"]): r["Title"].strip() for r in ex.get("Projects.csv", [])}
    # в LinkedIn названия обрастают пояснением («Maps to Waze — Telegram bot»)
    # или страной («Israeli Knesset…»), поэтому сверяем и вхождением, и началом
    def matched(a, pool):
        for b in pool:
            if a in b or b in a:
                return True
            if a[:10] and a[:10] == b[:10]:
                return True
        return False
    report("ЕСТЬ В CV, НЕТ В LINKEDIN:",
           [cv_names[k] for k in cv_names if not matched(k, li_names)])
    report("ЕСТЬ В LINKEDIN, НЕТ В CV:",
           [li_names[k] for k in li_names if not matched(k, cv_names)])

    # --- работа: сравниваем компании, не пытаясь свести дробление позиций ---
    cv_co = {norm(w["name"]): w["name"] for w in cv.get("work", [])}
    li_co = {norm(r["Company Name"]): r["Company Name"] for r in ex.get("Positions.csv", [])}
    report("КОМПАНИИ ТОЛЬКО В CV:",
           [cv_co[k] for k in cv_co if not matched(k, li_co)])
    report("КОМПАНИИ ТОЛЬКО В LINKEDIN:",
           [li_co[k] for k in li_co if not matched(k, cv_co)])

    # --- навыки: мусор и дубли ---
    li_sk = [r["Name"] for r in ex.get("Skills.csv", [])]
    cv_sk = {norm(k) for s in cv.get("skills", []) for k in s.get("keywords", [])}
    junk = [s for s in li_sk if s != s.strip()]
    dups = [s for s in li_sk
            if sum(1 for o in li_sk if norm(o) == norm(s) or
                   (norm(s) in norm(o) and norm(s) != norm(o))) > 1]
    report("НАВЫКИ В LINKEDIN — ФОРМАТ:",
           [f'"{s}" — пробел по краям' for s in junk] +
           [f'"{s}" — пересекается с другим пунктом' for s in sorted(set(dups))])
    report("НАВЫКИ ТОЛЬКО В LINKEDIN (проверь, нужны ли):",
           [s for s in li_sk if norm(s) not in cv_sk][:40])

    # --- headline и summary ---
    prof = (ex.get("Profile.csv") or [{}])[0]
    label = cv["basics"].get("label", "")
    if label and label not in (prof.get("Headline") or ""):
        report("HEADLINE:", [f'в LinkedIn нет должности из CV — "{label}"'])
        problems += 1

    print(f"\nитого замечаний, требующих правки в LinkedIn: {problems}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
