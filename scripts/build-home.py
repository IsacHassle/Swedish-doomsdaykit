#!/usr/bin/env python3
"""Builds web/index.html, the crisis kit start page.

It asks the running Kiwix server (port 8090) which libraries are installed,
checks that every emergency link really opens, and writes one page with:
search across all libraries, the AI page and the map, emergency topics, key
PDF books, all libraries, and the Swedish emergency numbers. Run by share-library.sh on start.
"""
import html
import json
import os
import re
import urllib.request

KIWIX = "http://localhost:8090"
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the kit folder
WEB = os.path.join(HOME, "web")
DOCS = os.path.join(HOME, "documents")

# (Swedish, English, article). Articles are looked up in WikiMed, then MDWiki.
EMERGENCY = [
    ("Hjärt-lungräddning", "CPR", "Cardiopulmonary_resuscitation"),
    ("Kraftig blödning", "Severe bleeding", "Bleeding"),
    ("Tryckförband, tourniquet", "Tourniquet", "Tourniquet"),
    ("Luftvägsstopp", "Choking", "Choking"),
    ("Chock", "Shock", "Shock_(circulatory)"),
    ("Brännskada", "Burn", "Burn"),
    ("Nedkylning", "Hypothermia", "Hypothermia"),
    ("Förfrysning", "Frostbite", "Frostbite"),
    ("Värmeslag", "Heat stroke", "Heat_stroke"),
    ("Allergisk chock", "Anaphylaxis", "Anaphylaxis"),
    ("Hjärtinfarkt", "Heart attack", "Myocardial_infarction"),
    ("Stroke", "Stroke", "Stroke"),
    ("Benbrott", "Fracture", "Bone_fracture"),
    ("Huvudskada", "Head injury", "Head_injury"),
    ("Sår", "Wounds", "Wound"),
    ("Blodförgiftning", "Sepsis", "Sepsis"),
    ("Uttorkning, diarré", "Dehydration", "Oral_rehydration_therapy"),
    ("Kolmonoxid (aggregat, kaminer)", "Carbon monoxide", "Carbon_monoxide_poisoning"),
    ("Förgiftning", "Poisoning", "Poisoning"),
    ("Svampförgiftning", "Mushroom poisoning", "Mushroom_poisoning"),
    ("Kramper", "Seizure", "Epileptic_seizure"),
    ("Lågt blodsocker", "Hypoglycemia", "Hypoglycemia"),
    ("Astma", "Asthma", "Asthma"),
    ("Drunkning", "Drowning", "Drowning"),
    ("Förlossning", "Childbirth", "Childbirth"),
    ("Huggormsbett", "Snakebite", "Snakebite"),
    ("Fästingar, TBE", "Tick-borne encephalitis", "Tick-borne_encephalitis"),
    ("Strålning, jodtabletter", "Radiation, iodine", "Potassium_iodide"),
    ("Panikångest", "Panic attack", "Panic_attack"),
]

# (label, description, path under documents/)
BOOKS = [
    ("Om krisen eller kriget kommer", "Myndighetens råd, på svenska", "Om-krisen-eller-kriget-kommer.pdf"),
    ("In case of crisis or war", "The same brochure in English", "In-case-of-crisis-or-war.pdf"),
    ("Where There Is No Doctor", "The classic village health care handbook", "library/Medical Library/Where there is no Doctor.pdf"),
    ("First Aid (Field Manual)", "Step-by-step first aid, US Army", "library/Military Medicine/First Aid (Field Manual).pdf"),
    ("Survival and Austere Medicine", "Medicine when there is no hospital", "library/Medical Library/Survival and Austere Medicine.pdf"),
    ("Family Guide to Emergency Health Care", "Care at home for the family", "library/Military Medicine/Family Guide to Emergency Health Care.pdf"),
    ("Emergency Childbirth", "Delivering a baby without a hospital", "library/Military Medicine/Emergency Childbirth.pdf"),
    ("Where There Is No Dentist", "Tooth pain, infections, extractions", "library/Medical Library/Where There is No Dentist.pdf"),
    ("Purifying Water During an Emergency", "Making water safe to drink", "library/Water Treatment/Purifying Water During an Emergency.pdf"),
    ("Bandaging and Splinting", "Dressings, slings and splints", "library/Military Medicine/Bandaging and Splinting.pdf"),
]

# Library groups: (heading, [(book name prefix, short Swedish description)])
GROUPS = [
    ("Sjukvård · Medical", [
        ("wikipedia_en_medicine", "Alla medicinska Wikipedia-artiklar, med bilder"),
        ("mdwiki_en", "Granskat medicinskt uppslagsverk"),
        ("zimgit-medicine", "Böcker: akutsjukvård, Where There Is No Doctor"),
        ("irp.fas.org_en_military-medicine", "Fältsjukvård, trauma, blödning"),
        ("medlineplus", "Sjukdomar och läkemedel, lättläst"),
        ("nhs.uk_en_medicines", "Läkemedel: vad de är till för, biverkningar"),
        ("wwwnc.cdc.gov", "Smittsamma sjukdomar och utbrott"),
    ]),
    ("Vatten, mat, skydd · Water, food, shelter", [
        ("zimgit-water", "Rena vatten: koka, filtrera, kemiskt"),
        ("zimgit-food-preparation", "Förvara och laga mat utan el"),
        ("zimgit-post-disaster", "Skydd, sanitet, återuppbyggnad"),
        ("solar.lowtechmagazine", "Värme och matlagning utan el"),
        ("www.ready.gov", "Beredskap för olika katastrofer"),
        ("cd3wdproject", "Lågteknik: odling, vatten, energi, bygg"),
        ("appropedia", "Hållbar självförsörjning, praktiska projekt"),
        ("cooking.stackexchange", "Frågor och svar om matlagning"),
        ("gardening.stackexchange", "Frågor och svar om odling"),
        ("outdoors.stackexchange", "Friluftsliv, skydd, värme"),
        ("zimgit-knots", "Knopar och surrningar"),
    ]),
    ("Laga och kommunicera · Repair and radio", [
        ("ifixit", "Reparationsguider för allt"),
        ("mechanics.stackexchange", "Bilreparationer"),
        ("diy.stackexchange", "Hus: värme, vatten, el"),
        ("ham.stackexchange", "Amatörradio och nödkommunikation"),
    ]),
    ("Allmän kunskap · General knowledge", [
        ("wikipedia_sv_all", "Svenska Wikipedia, med bilder"),
        ("wikipedia_en_all", "English Wikipedia, text only"),
    ]),
]


def kiwix_ok(path):
    try:
        req = urllib.request.Request(KIWIX + path, method="HEAD")
        return urllib.request.urlopen(req, timeout=5).status in (200, 302)
    except Exception:
        return False


def catalog():
    try:
        x = urllib.request.urlopen(KIWIX + "/catalog/v2/entries?count=500", timeout=10).read().decode()
    except Exception:
        return []
    books = []
    for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
        name = re.search(r'href="/content/([^"/]+)', e)
        lang = re.search(r"<language>(.*?)</language>", e)
        title = re.search(r"<title>(.*?)</title>", e, re.S)
        if name:
            books.append({"name": name.group(1), "lang": lang.group(1) if lang else "",
                          "title": html.unescape(title.group(1)) if title else name.group(1)})
    return books


def main():
    books = catalog()
    by_prefix = lambda p: next((b for b in books if b["name"].startswith(p)), None)
    eng = [b["name"] for b in books if b["lang"] == "eng"]
    swe = [b["name"] for b in books if b["lang"] == "swe"]

    med_books = [b for b in (by_prefix("wikipedia_en_medicine"), by_prefix("mdwiki_en")) if b]
    emergency = []
    for sv, en, art in EMERGENCY:
        for b in med_books:
            path = f"/content/{b['name']}/{art}"
            if kiwix_ok(path):
                emergency.append((sv, en, f"/viewer#{b['name']}/{art}"))
                break

    books_html = []
    for label, desc, rel in BOOKS:
        if os.path.exists(os.path.join(DOCS, rel)):
            href = "docs/" + "/".join(urllib.request.quote(p) for p in rel.split("/"))
            books_html.append(f'<a class="card" href="{href}"><b>{html.escape(label)}</b><span>{html.escape(desc)}</span></a>')

    groups_html = []
    shown = set()
    for heading, items in GROUPS:
        cards = []
        for prefix, desc in items:
            b = by_prefix(prefix)
            if not b:
                continue
            shown.add(b["name"])
            cards.append(f'<a class="card" data-k="/viewer#{b["name"]}"><b>{html.escape(b["title"])}</b><span>{html.escape(desc)}</span></a>')
        if cards:
            groups_html.append(f'<h3>{html.escape(heading)}</h3><div class="grid">{"".join(cards)}</div>')
    extra = [b for b in books if b["name"] not in shown]
    if extra:
        cards = "".join(f'<a class="card" data-k="/viewer#{b["name"]}"><b>{html.escape(b["title"])}</b><span>{html.escape(b["name"])}</span></a>' for b in extra)
        groups_html.append(f'<h3>Övrigt · Other</h3><div class="grid">{cards}</div>')

    emergency_html = "".join(
        f'<a class="chip" data-k="{html.escape(k)}"><b>{html.escape(sv)}</b><span>{html.escape(en)}</span></a>'
        for sv, en, k in emergency)

    page = TEMPLATE
    for key, val in {
        "%EMERGENCY%": emergency_html or "<p>Starta delningen så att biblioteket är igång.</p>",
        "%BOOKS%": "".join(books_html),
        "%GROUPS%": "".join(groups_html) or "<p>Inga bibliotek hittades. Kör share-library.sh.</p>",
        "%ENG%": json.dumps(eng),
        "%SWE%": json.dumps(swe),
        "%COUNT%": str(len(books)),
    }.items():
        page = page.replace(key, val)
    os.makedirs(WEB, exist_ok=True)
    with open(os.path.join(WEB, "index.html"), "w") as f:
        f.write(page)
    print(f"Start page built: {len(books)} libraries, {len(emergency)} emergency topics, {len(books_html)} books.")


TEMPLATE = r"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Krislåda</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E%E2%9B%91%3C/text%3E%3C/svg%3E">
<style>
  :root { --bg:#f6f5f2; --fg:#1d1d1f; --muted:#5f5f66; --card:#ffffff; --line:#e3e1dc; --accent:#0b5cad; --fill:#0b5cad; --red:#b3261e; --redbg:#fdecea; }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#141416; --fg:#f2f2f4; --muted:#a3a3ab; --card:#1f1f23; --line:#2e2e34; --accent:#6aa9ff; --fill:#1f5fae; --red:#ff8a80; --redbg:#3a1d1b; }
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.45 -apple-system, system-ui, "Segoe UI", sans-serif; }
  main { max-width: 1100px; margin: 0 auto; padding: 16px; }
  h1 { font-size: 26px; margin: 4px 0 2px; }
  h2 { font-size: 19px; margin: 28px 0 10px; }
  h3 { font-size: 15px; margin: 20px 0 8px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
  .sub { color: var(--muted); margin: 0 0 14px; }
  .alert { background: var(--redbg); border: 1px solid var(--red); border-radius: 12px; padding: 12px 14px; }
  .alert b { color: var(--red); }
  .nums { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 6px; }
  .nums span { white-space: nowrap; }
  form.search { display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }
  form.search input { flex: 1 1 260px; font-size: 18px; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--line); background: var(--card); color: var(--fg); }
  form.search button { font-size: 16px; padding: 12px 16px; border-radius: 10px; border: 0; background: var(--fill); color: #fff; cursor: pointer; }
  form.search button.alt { background: var(--card); color: var(--fg); border: 1px solid var(--line); }
  .chips { display: grid; grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)); gap: 8px; }
  .chip, .card { display: block; background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; color: var(--fg); text-decoration: none; cursor: pointer; }
  .chip:hover, .card:hover { border-color: var(--accent); }
  .chip b, .card b { display: block; }
  .chip span, .card span { display: block; color: var(--muted); font-size: 14px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 8px; }
  .big { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 8px; }
  .big a { background: var(--fill); color: #fff; border: 0; }
  .big a span { color: #e8f0ff; }
  .big.top { margin-top: 14px; }
  .big.top a b { font-size: 18px; }
  footer { color: var(--muted); font-size: 14px; margin: 32px 0 12px; }
</style>
</head>
<body>
<main>
  <h1>Krislåda</h1>
  <p class="sub">Allt här fungerar utan internet. %COUNT% bibliotek, karta och böcker. · Everything here works offline.</p>

  <div class="alert">
    <b>Livsfara? Ring 112</b> om någon telefon fungerar, även utan SIM-kort.
    <div class="nums">
      <span><b>112</b> nödsituation</span>
      <span><b>1177</b> sjukvårdsrådgivning</span>
      <span><b>113 13</b> information vid kris</span>
      <span><b>114 14</b> polis, ej akut</span>
      <span>Radio: <b>Sveriges Radio P4</b></span>
    </div>
  </div>

  <form class="search" id="search">
    <input id="q" placeholder="Sök i alla bibliotek, t.ex. hypothermia, water purification" autocomplete="off" aria-label="Sök">
    <button type="submit">Sök (engelska)</button>
    <button type="button" class="alt" id="sv">Sök på svenska</button>
  </form>
  <p class="sub" style="margin-top:6px">De flesta böcker är på engelska: sök med engelska ord. Eller fråga AI:n på svenska, den läser böckerna åt dig.</p>

  <div class="big top">
    <a class="card" href="ai/"><b>🤖 Fråga AI · Ask the AI</b><span>Skriv eller prata på svenska. Svarar ur böckerna och visar källan, kan titta på foton. Guide på sidan.</span></a>
    <a class="card" href="map/"><b>🗺 Karta · Map</b><span>Sök gata och adress, hitta närmaste sjukhus, apotek och dricksvatten.</span></a>
  </div>

  <h2>Akut · Emergency</h2>
  <div class="chips">%EMERGENCY%</div>

  <h2>Viktigaste böckerna · Key books</h2>
  <div class="grid">%BOOKS%</div>

  <h2>Karta och dokument · Map and documents</h2>
  <div class="big">
    <a class="card" href="map/"><b>Karta över Sverige</b><span>Zooma in till enskilda hus. Sök adress, tryck för koordinater</span></a>
    <a class="card" href="docs/"><b>Alla dokument</b><span>Broschyrer och hela boksamlingen som PDF</span></a>
  </div>

  <h2>Alla bibliotek · All libraries</h2>
  %GROUPS%

  <footer>Krislåda · Swedish-doomsdaykit · Start: Start Crisis Kit.command · Libraries by Kiwix, map © OpenStreetMap</footer>
</main>
<script>
  const KIWIX = location.protocol + '//' + (location.hostname || 'localhost') + ':8090';
  const ENG = %ENG%, SWE = %SWE%;
  document.querySelectorAll('[data-k]').forEach(a => a.href = KIWIX + a.dataset.k);
  const go = books => {
    const q = document.getElementById('q').value.trim();
    if (!q || !books.length) return;
    location.href = KIWIX + '/search?pattern=' + encodeURIComponent(q) + books.map(b => '&books.name=' + encodeURIComponent(b)).join('');
  };
  document.getElementById('search').addEventListener('submit', e => { e.preventDefault(); go(ENG); });
  document.getElementById('sv').addEventListener('click', () => go(SWE.length ? SWE : ENG));
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
