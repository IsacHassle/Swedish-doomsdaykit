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
# Where a Swedish authority page on the same thing is saved (scripts/fetch-swedish-pages.py),
# the button opens that page in Swedish, with the English article one tap away.
SWEDISH = {
    'Cardiopulmonary_resuscitation': '1177 - Hjärt-lungräddning',
    'Bleeding': '1177 - Stoppa en blödning',
    'Tourniquet': 'MCF - Stoppa en blödning',
    'Choking': '1177 - Om någon sätter i halsen',
    'Shock_(circulatory)': '1177 - Chock',
    'Burn': '1177 - Brännskador',
    'Frostbite': '1177 - Köldskador – förfrysning',
    'Heat_stroke': '1177 - Värmeslag',
    'Anaphylaxis': '1177 - Allergisk chock – anafylaxi',
    'Head_injury': '1177 - Hjärnskakning',
    'Wound': '1177 - Behandling av stora sår',
    'Carbon_monoxide_poisoning': '1177 - Inandning av skadlig gas',
    'Poisoning': '1177 - Förgiftning',
    'Drowning': '1177 - Drunkningsolyckor',
    'Snakebite': '1177 - Huggormsbett',
    'Tick-borne_encephalitis': '1177 - Fästingbett',
    'Potassium_iodide': 'MCF - Varning kring Sveriges kärnkraftverk',
}
SV_DIR = "library/Svenska myndigheter"
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
    ("Sjukvård", [
        ("wikipedia_en_medicine", "Alla medicinska Wikipedia-artiklar, med bilder"),
        ("mdwiki_en", "Granskat medicinskt uppslagsverk"),
        ("zimgit-medicine", "Böcker: akutsjukvård, Where There Is No Doctor"),
        ("irp.fas.org_en_military-medicine", "Fältsjukvård, trauma, blödning"),
        ("medlineplus", "Sjukdomar och läkemedel, lättläst"),
        ("nhs.uk_en_medicines", "Läkemedel: vad de är till för, biverkningar"),
        ("wwwnc.cdc.gov", "Smittsamma sjukdomar och utbrott"),
    ]),
    ("Vatten, mat och skydd", [
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
    ("Laga och kommunicera", [
        ("ifixit", "Reparationsguider för allt"),
        ("mechanics.stackexchange", "Bilreparationer"),
        ("diy.stackexchange", "Hus: värme, vatten, el"),
        ("ham.stackexchange", "Amatörradio och nödkommunikation"),
    ]),
    ("Allmän kunskap", [
        ("wikipedia_sv_all", "Svenska Wikipedia, med bilder"),
        ("wikipedia_en_all", "English Wikipedia, text only"),
    ]),
]


ADVICE_ORDER = ["1177", "MCF", "Livsmedelsverket", "Krisinformation"]
ADVICE_NAMES = {"1177": "1177 · Första hjälpen och skador", "MCF": "MCF · Hemberedskap, varningar, skyddsrum, brand",
                "Livsmedelsverket": "Livsmedelsverket · Vatten och mat", "Krisinformation": "Krisinformation.se"}
ADVICE_COUNT = 0


def swedish_page(stem):
    """(link to the reader page, authority) for a saved Swedish page, or (None, None)."""
    if not stem or not os.path.exists(os.path.join(DOCS, SV_DIR, stem + ".md")):
        return (None, None)
    rel = "docs/" + SV_DIR + "/" + stem + ".md"
    return ("las/?f=" + urllib.request.quote(rel), stem.split(" - ", 1)[0])


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
                emergency.append((sv, en, f"/viewer#{b['name']}/{art}", swedish_page(SWEDISH.get(art))))
                break

    # Swedish authorities' advice, grouped by authority.
    advice = {}
    folder = os.path.join(DOCS, SV_DIR)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith(".md") and " - " in name:
            src, title = name[:-3].split(" - ", 1)
            advice.setdefault(src, []).append((title, swedish_page(name[:-3])))
    advice_html = "".join(
        f'<h3 class="sub">{html.escape(ADVICE_NAMES.get(src, src))}</h3><div class="tabs plain">'
        + "".join(f'<a class="tab" href="{href}"><b>{html.escape(t)}</b></a>' for t, href in items) + "</div>"
        for src, items in sorted(advice.items(), key=lambda kv: ADVICE_ORDER.index(kv[0]) if kv[0] in ADVICE_ORDER else 99))

    books_html = []
    for label, desc, rel in BOOKS:
        if os.path.exists(os.path.join(DOCS, rel)):
            href = "docs/" + "/".join(urllib.request.quote(p) for p in rel.split("/"))
            books_html.append(f'<a class="tile" href="{href}"><span class="k">PDF · bok {len(books_html) + 1:02d}</span>'
                              f'<b>{html.escape(label)}</b><span class="d">{html.escape(desc)}</span></a>')

    groups_html = []
    shown = set()
    for heading, items in GROUPS:
        cards = []
        for prefix, desc in items:
            b = by_prefix(prefix)
            if not b:
                continue
            shown.add(b["name"])
            cards.append(f'<a class="tile" data-k="/viewer#{b["name"]}"><span class="k">Bibliotek</span>'
                         f'<b>{html.escape(b["title"])}</b><span class="d">{html.escape(desc)}</span></a>')
        if cards:
            groups_html.append(f'<h3 class="sub">{html.escape(heading)}</h3><div class="tiles">{"".join(cards)}</div>')
    extra = [b for b in books if b["name"] not in shown]
    if extra:
        cards = "".join(f'<a class="tile" data-k="/viewer#{b["name"]}"><span class="k">Bibliotek</span><b>{html.escape(b["title"])}</b>'
                        f'<span class="d">{html.escape(b["name"])}</span></a>' for b in extra)
        groups_html.append(f'<h3 class="sub">Övrigt</h3><div class="tiles">{cards}</div>')

    emergency_html = "".join(
        (f'<div class="tab"><a class="main" href="{sv_href}"><b>{html.escape(sv)}</b><span class="src">{html.escape(sv_src)}</span></a>'
         f'<a class="en" data-k="{html.escape(k)}">På engelska: {html.escape(en)}</a></div>')
        if sv_href else
        f'<a class="tab" data-k="{html.escape(k)}"><b>{html.escape(sv)}</b><span class="src">WikiMed · engelska</span></a>'
        for sv, en, k, (sv_href, sv_src) in emergency)

    page = TEMPLATE
    for key, val in {
        "%EMERGENCY%": emergency_html or "<p>Starta delningen så att biblioteket är igång.</p>",
        "%ADVICE%": advice_html or "<p>Kör installationen för att hämta myndigheternas råd.</p>",
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
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/icon-180.png">
<meta name="apple-mobile-web-app-title" content="Krislåda">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#161512">
<link rel="icon" href="/icon-180.png">
<link rel="stylesheet" href="lib/kit.css">
<style>
  form.search { display: flex; gap: 8px; flex-wrap: wrap; }
  form.search input { flex: 1 1 280px; }
</style>
</head>
<body>
<header class="topbar"><div class="wrap">
  <a class="logo" href="./">Krislåda<small>SVERIGE · OFFLINE</small></a>
  <div class="meta"><span id="clock"></span><br>%COUNT% bibliotek · karta · AI</div>
</div></header>
<div class="hazard"></div>

<main>
  <div class="danger">
    <div class="body">
      <div class="call">Livsfara? <b>Ring 112</b></div>
      <div class="nums">
        <span><b>112</b>nödsituation</span>
        <span><b>1177</b>sjukvårdsråd</span>
        <span><b>113&nbsp;13</b>information vid kris</span>
        <span><b>114&nbsp;14</b>polisen, ej akut</span>
        <span>Radio: <b>P4</b></span>
      </div>
    </div>
  </div>
  <div class="warn" id="battery" hidden></div>

  <div class="sec"><span class="num">01</span><h2>Akut</h2><span class="hint">Första hjälpen, steg för steg</span></div>
  <div class="tabs">%EMERGENCY%</div>

  <div class="sec"><span class="num">02</span><h2>Verktyg</h2></div>
  <div class="tiles tools">
    <a class="tile go" href="ai/"><span class="k">AI · offline</span><b>Fråga AI</b><span class="d">Skriv eller prata på svenska. Svarar ur böckerna och visar källan.</span></a>
    <a class="tile" href="map/"><span class="k">Karta · hela Sverige</span><b>Karta</b><span class="d">Sök ort, gata och adress. Närmaste sjukhus, apotek och vatten.</span></a>
    <a class="tile olive" href="map/?gps=1"><span class="k">GPS</span><b>Var är jag?</b><span class="d">Din position på kartan, med USB GPS-mottagare eller mobilen.</span></a>
    <a class="tile" href="skriv-ut/"><span class="k">Papper</span><b>Skriv ut</b><span class="d">Första hjälpen, varningar, vatten och värme. Gör det nu.</span></a>
    <a class="tile" href="checklista/"><span class="k">Hemberedskap</span><b>Checklista</b><span class="d">Har du det du behöver för en vecka?</span></a>
  </div>

  <div class="sec"><span class="num">03</span><h2>Sök i biblioteken</h2></div>
  <form class="search" id="search">
    <input type="search" id="q" placeholder="t.ex. hypothermia, water purification, kantarell" autocomplete="off" aria-label="Sök i biblioteken">
    <button type="submit" class="btn go">Sök (engelska)</button>
    <button type="button" class="btn ghost" id="sv">Sök på svenska</button>
  </form>
  <p class="lead" style="margin-top:8px">De flesta böcker är på engelska, så sök med engelska ord. Eller fråga AI:n på svenska.</p>

  <div class="sec"><span class="num">04</span><h2>Myndigheternas råd</h2><span class="hint">1177 · MCF · Livsmedelsverket, sparade för läsning utan internet</span></div>
  %ADVICE%

  <div class="sec"><span class="num">05</span><h2>Böcker</h2><span class="hint">De viktigaste, som PDF</span></div>
  <div class="tiles">%BOOKS%
    <a class="tile" href="docs/"><span class="k">Alla filer</span><b>Alla dokument</b><span class="d">Broschyrer och hela boksamlingen</span></a>
  </div>

  <div class="sec"><span class="num">06</span><h2>Alla bibliotek</h2></div>
  %GROUPS%

  <footer class="kit">KRISLÅDA · Swedish-doomsdaykit · Starta: Starta Krislåda.command · Kontrollera en gång i månaden: Kontrollera Krislåda.command<br>
  Bibliotek från Kiwix · Karta © OpenStreetMap · Råd från 1177, MCF och Livsmedelsverket</footer>
</main>
<script>
  const KIWIX = 'http://' + (location.hostname || 'localhost') + ':8090';   // the libraries are always plain http
  const ENG = %ENG%, SWE = %SWE%;
  document.querySelectorAll('[data-k]').forEach(a => a.href = KIWIX + a.dataset.k);
  const go = books => {
    const q = document.getElementById('q').value.trim();
    if (!q || !books.length) return;
    location.href = KIWIX + '/search?pattern=' + encodeURIComponent(q) + books.map(b => '&books.name=' + encodeURIComponent(b)).join('');
  };
  document.getElementById('search').addEventListener('submit', e => { e.preventDefault(); go(ENG); });
  document.getElementById('sv').addEventListener('click', () => go(SWE.length ? SWE : ENG));
  const clock = () => { document.getElementById('clock').textContent = new Date().toLocaleString('sv-SE', { dateStyle: 'medium', timeStyle: 'short' }); };
  clock(); setInterval(clock, 30000);
  // On battery: say so, with what saves power.
  const battery = () => fetch('/ai-api/status').then(r => r.json()).then(s => {
    const b = s.battery, el = document.getElementById('battery');
    if (b && b.on_battery) {
      el.hidden = false;
      el.innerHTML = `Macen går på batteri: ${b.percent} %. Spara ström: sänk ljusstyrkan, stäng andra appar, välj <b>Spara batteri</b> i AI:n och ställ få frågor.`;
    } else el.hidden = true;
  }).catch(() => {});
  battery(); setInterval(battery, 60000);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
