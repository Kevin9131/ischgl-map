#!/usr/bin/env python3
"""Mirror the official Ischgl/Samnaun lift & piste status into status.json.

Runs from a GitHub Action. Reads the public "slopes & facilities" page on
ischgl.com, extracts every lift (by its code, e.g. A1, B8) and piste (by
number + difficulty) with its open/closed state, and writes status.json.
The file is only rewritten when something actually changed, so the repo
doesn't get a commit every 15 minutes.

Usage: python fetch_status.py [local_html_file_for_testing]
"""
import datetime, json, os, re, sys, urllib.request
from bs4 import BeautifulSoup

# 1st choice: the Intermaps feed behind the official Ischgl skimap/app (JSON)
FEED = "https://winter.intermaps.com/silvretta_arena/data?lang=en"
# fallback: the official "open facilities" web page (HTML)
URLS = [
    "https://www.ischgl.com/en/winter/silvretta-arena/open-facilities",
    "https://www.ischgl.com/en/Active/Active-Winter/Skiing-in-Ischgl/Slopes-Facilities",
]
# official lift codes and the names they go by (feed / website / OpenStreetMap)
CODES = {
 "A1": ["Silvrettabahn"], "A2": ["Pardatschgratbahn"], "A3": ["Fimbabahn"], "B1": ["Velillbahn"],
 "B2": ["Flimjochbahn"], "B3": ["Idjochbahn"], "B4": ["Greitspitzlift"], "B5": ["Sonnenbahn"],
 "B6": ["Übungslift Velill"], "B7": ["Übungslift Viderböden"], "B8": ["Gratbahn"], "B9": ["Förderband Übungsareal"],
 "B10": ["Förderband Viderböden"], "C1": ["Höllbodenbahn"], "C2": ["Höllkarbahn"], "C3": ["Sassgalunbahn"],
 "C4": ["Nachtweidebahn"], "C5": ["Lange Wandbahn"], "D1": ["Palinkopfbahn"], "D2": ["Zeblasbahn"],
 "E1": ["Paznauner Thayabahn", "Paznauner Tajabahn"], "E2": ["Höllspitzbahn"], "E3": ["Bodenalpbahn"], "E4": ["Gampenbahn"],
 "E5": ["Piz Val Grondabahn"], "F1": ["Velilleckbahn"], "F2": ["Pardoramabahn"], "G1": ["Übungslift Mathon"],
 "G2": ["Schwarzwasserlift"], "L1": ["Doppelstöckige Pendelbahn", "Twinliner"], "L2": ["Luftseilbahn", "Luftseilbahn Samnaun"],
 "L3": ["Laretbahn"], "M1": ["Grivaleabahn"], "M2": ["Mullerbahn"], "N1": ["Flimsattelbahn"], "N2": ["Visnitzbahn"],
 "N3": ["Milolift"], "N4": ["Viderjochbahn 1"], "N5": ["Alp Trider Ecklift"], "N6": ["Alp Trider Sattelbahn", "Alp Trida Sattelbahn"],
 "O1": ["Greitspitzbahn"], "O2": ["Blais Grondalift"], "O4": ["Viderjochbahn 2"], "P1": ["Musellalift"],
 "P2": ["Förderband Musella 1"], "P3": ["Förderband Musella 2"],
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
LETTER = {"E": "blue", "M": "red", "S": "black"}  # easy / medium / schwer


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (personal piste-map status mirror; github.com/Kevin9131/ischgl-map)",
        "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def norm(x):
    return re.sub(r"[^a-z0-9äöüß]", "", (x or "").lower())


NAME2CODE = {norm(n): c for c, ns in CODES.items() for n in ns}


def code_for(title):
    t = (title or "").strip()
    m = re.match(r"^([A-P]\d{1,2})\b[\s\-–]*(.*)$", t)
    if m and m.group(1) in CODES:
        return m.group(1), m.group(2) or t
    n = norm(re.sub(r"\(.*?\)", "", t))
    if n in NAME2CODE:
        return NAME2CODE[n], t
    for k, c in NAME2CODE.items():  # e.g. "Milolift (Übungslift)"
        if k and (n.startswith(k) or k.startswith(n)) and min(len(k), len(n)) >= 6:
            return c, t
    return None, t


def word(raw):
    w = (raw or "").lower()
    if "closed" in w or "geschlossen" in w or w == "unknown":
        return "closed" if w != "unknown" else "unknown"
    if "prep" in w or "vorbereitung" in w:
        return "prep"
    if w.startswith("open") or "partially_open" in w or "geöffnet" in w:
        return "open"
    return "unknown"


def colour_for(*texts):
    t = " ".join(str(x) for x in texts if x).lower()
    if "easy" in t or "leicht" in t or "blue" in t:
        return "blue"
    if "medium" in t or "intermediate" in t or "mittel" in t or "red" in t:
        return "red"
    if "difficult" in t or "schwer" in t or "black" in t or "expert" in t:
        return "black"
    if "route" in t or "freeride" in t:
        return "route"
    return "other"


def parse_feed(data):
    lifts, slopes = {}, {}
    for row in data.get("lifts") or []:
        title = (row.get("popup") or {}).get("title") or row.get("title")
        code, name = code_for(title)
        if code:
            s = word(row.get("status") or (row.get("popup") or {}).get("status"))
            if code not in lifts or s == "open":
                lifts[code] = {"name": name, "s": s}
    for group in ("slopes", "routes"):
        for row in data.get(group) or []:
            p = row.get("popup") or {}
            title = (p.get("title") or "").strip()
            m = re.match(r"^(\d{1,3}[a-c]?)\.?\s*[-–]?\s*(.*)$", title)
            if not m:
                continue
            colour = colour_for(row.get("subtitle"), p.get("subtitle"), row.get("type"))
            if group == "routes" and colour == "other":
                continue  # hiking / toboggan routes
            key = f"{m.group(1)}|{colour}"
            s = word(row.get("status") or p.get("status"))
            if key not in slopes or s == "open":
                slopes[key] = {"name": m.group(2), "s": s}
    return lifts, slopes, data.get("lastUpdate")


def state(td):
    st = td.find(class_="status")
    if not st:
        return "unknown"
    txt = " ".join([st.get("aria-label") or "", st.get("title") or ""] + (st.get("class") or [])).lower()
    if "closed" in txt or "geschlossen" in txt:
        return "closed"
    if "prep" in txt or "vorbereitung" in txt or "reserved" in txt:
        return "prep"
    if "open" in txt or "geöffnet" in txt or "offen" in txt:
        return "open"
    return "unknown"


def rows(soup, panel_id):
    panel = soup.find(id=panel_id)
    if not panel:
        return []
    out = []
    for tr in panel.select(".table-responsive > .table-fixed > tbody > tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) >= 3:  # skip the collapsed "details" rows
            out.append(tds)
    return out


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    lifts, slopes = {}, {}
    for tds in rows(soup, "facility-lifts"):
        ref = " ".join(tds[1].get_text().split())
        name = tds[2].get_text(strip=True)
        if ref:
            lifts[ref] = {"name": name, "s": state(tds[0])}
    for tds in rows(soup, "facility-slopes"):
        letter = tds[1].find(class_="status__letter")
        colour = LETTER.get(letter.get_text(strip=True) if letter else "", "other")
        text = " ".join(tds[1].get_text().split())
        num = text[1:].strip().rstrip(".") if letter else text.rstrip(".")
        name = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        key = f"{num or name}|{colour}"
        s = state(tds[0])
        # the same number can appear twice (e.g. "1" and "1."); open wins
        if key not in slopes or s == "open":
            slopes[key] = {"name": name, "s": s}
    m = re.search(r"(?:Last update|Letzte Aktualisierung)\D{0,20}(\d{1,2}\.\d{1,2}\.\d{4})[ ,]*(\d{1,2}:\d{2})?", soup.get_text(" "))
    resort_update = " ".join(x for x in (m.group(1), m.group(2)) if x) if m else None
    return lifts, slopes, resort_update


def main():
    lifts, slopes, upd, src = {}, {}, None, None
    if len(sys.argv) > 1:  # local test file: .json = feed, otherwise HTML page
        txt = open(sys.argv[1], encoding="utf-8").read()
        lifts, slopes, upd = parse_feed(json.loads(txt)) if sys.argv[1].endswith(".json") else parse(txt)
        src = "local file"
    else:
        try:
            lifts, slopes, upd = parse_feed(json.loads(fetch(FEED)))
            src = FEED
            print(f"feed: {len(lifts)} lifts, {len(slopes)} pistes")
        except Exception as e:
            print("feed failed:", e, file=sys.stderr)
        if len(lifts) < 20:
            for u in URLS:
                try:
                    l2, s2, u2 = parse(fetch(u))
                    print(f"page {u}: {len(l2)} lifts, {len(s2)} pistes")
                    if len(l2) > len(lifts):
                        lifts, slopes, upd, src = l2, s2, u2, u
                    if len(lifts) >= 20:
                        break
                except Exception as e:
                    print("page failed:", u, e, file=sys.stderr)
    if len(lifts) < 20:
        sys.exit(f"page layout changed? only {len(lifts)} lifts found; keeping old status.json")
    new = {"source": src, "resortUpdate": upd, "lifts": lifts, "slopes": slopes}
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            pass
    same = all(old.get(k) == new[k] for k in ("resortUpdate", "lifts", "slopes"))
    n_open = sum(v["s"] == "open" for v in lifts.values())
    print(f"{n_open}/{len(lifts)} lifts open, {sum(v['s']=='open' for v in slopes.values())}/{len(slopes)} pistes open, resort update {upd}")
    if same:
        print("no change")
        return
    new["changed"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("status.json updated")


if __name__ == "__main__":
    main()
