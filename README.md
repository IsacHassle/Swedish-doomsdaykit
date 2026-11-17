# Swedish-doomsdaykit · Krislåda

An offline crisis kit for Sweden, on a Mac. When the internet, the phone network or the power grid is down, it still gives you:

- **First aid and medicine:** 29 one-tap emergency topics, medical encyclopedias, field medicine handbooks and the NHS medicines guide
- **A local AI you can ask in Swedish**, which answers from the kit's books and shows its sources, and can look at photos
- **A map of all of Sweden** down to single houses, with search for every town, street and address, and the nearest hospital, pharmacy, police, drinking water, food and fuel
- **What to do in each kind of emergency:** the Swedish government brochure *Om krisen eller kriget kommer*, and guides for radiation, chemical incidents, power cuts, winter storms and more
- **Phones on the same Wi-Fi can use all of it too.** The Mac does the work, no internet needed

*På svenska:* En krislåda för Mac som fungerar helt utan internet. Sjukvårdsråd, en AI du kan fråga på svenska, karta över hela Sverige med adressök, och myndigheternas råd. Mobiler på samma wifi kan använda allt. Installera med `./install.sh`.

Everything runs on your own computer. Nothing is sent anywhere.

## Install

You need a Mac with Apple Silicon (M1 or newer), about **50 GB** free (16 GB RAM or more recommended for the AI), and an internet connection while installing. It takes a few hours, mostly downloading.

```bash
git clone https://github.com/IsacHassle/Swedish-doomsdaykit.git ~/Crisis
cd ~/Crisis
./install.sh
```

(Or download the ZIP from GitHub, unzip it, and run `./install.sh` in that folder.)

The installer downloads everything from the original sources, checks every library against its published checksum, installs **Ollama** and **AnythingLLM** if they are missing, sets up the AI, and puts a **Crisis Kit** shortcut on the Desktop. If anything stops, run `./install.sh` again: it carries on where it stopped. `./install.sh --no-ai` installs everything except the AI (about 20 GB).

The first time AnythingLLM opens it may show a welcome screen: click through it, then run `./install.sh` again if the AI step stopped there.

When it is done: **print `Krislåda - guide to print.pdf`** and keep it with your emergency supplies. If the Mac is out of power, paper is the copy you can still read.

---

Everything below is the user guide. The same text is in the printable PDF, and the AI has read it too.

## Start here

1. Double-click **Start Crisis Kit.command** (in the kit folder, or the **Crisis Kit** shortcut on the Desktop). It also starts the AI apps Ollama and AnythingLLM in the background. Keep the Terminal window it opens.
2. The **start page** opens in your browser at http://localhost:8091. It has:
    - **one search box** across every library (English words work best; there is a Swedish button too)
    - **🤖 Fråga AI**: ask the AI in Swedish, see the guide below
    - **🗺 Karta**: the map of Sweden, with address search
    - **29 emergency buttons**: CPR, bleeding, burns, hypothermia, carbon monoxide, poisoning, childbirth and more
    - **the 10 key books** as PDFs, and **all documents**
3. **Family phones:** join the same Wi-Fi and open the address the Terminal window prints (for example `http://192.168.1.23:8091`). No internet needed. The AI and the map work from phones too; the Mac does the work. A router on battery power works, and so does the Mac's own hotspot.

| I need to... | Do this |
|---|---|
| Act fast on an injury or illness | Start page → **Akut** button. Call **112** if any phone works |
| Ask a question in plain Swedish or English | Start page → **🤖 Fråga AI**. It answers from the books and names its sources |
| Ask about a photo (wound, rash, plant, broken part) | **🤖 Fråga AI** → **📷 Foto** |
| Ask without typing | Mac dictation: the 🎤 key, or press Fn twice. On a phone, the keyboard's microphone |
| Know what Swedish authorities advise | Start page → *Om krisen eller kriget kommer* |
| Find an address, the nearest hospital, pharmacy or drinking water | Start page → **🗺 Karta** → search box or the 🏥 💊 🚰 buttons |
| Read coordinates to pass on | **🗺 Karta** → tap the map |
| Hear official warnings | Battery or crank radio on **Sveriges Radio P4** |

Swedish numbers: **112** emergency · **1177** health advice · **113 13** crisis information · **114 14** police, non-urgent.

## Using the AI

The AI runs entirely on the Mac. Open it from the start page: **🤖 Fråga AI** (or go straight to http://localhost:8091/ai/). The same page works on family phones on the Wi-Fi.

1. **Pick a mode** at the top of the page:

    | Mode | Use it for | Speed |
    |---|---|---|
    | 📚 **Svar ur böckerna** (answers from the books) | Most questions: injuries, illness, medicines, water, food, heat, official advice. It reads the kit's books (medical handbooks, NHS medicines, water treatment, food, MCF brochure, Ready.gov guides) and lists the books it used under the answer; tap one to open it | About 10 to 40 s |
    | ⚡ **Snabbt svar** (quick) | When it is urgent, or to ask about a **photo**. Same large model, without the books | About 5 to 20 s |
    | 🔋 **Spara batteri** (battery saver) | When the Mac is on battery and you do not know when you can charge. Smaller model, simpler answers, also takes photos | Faster, lighter |

2. **Write like you are calling 1177.** Who (age, weight for children), what happened, when, what you see, what you have at home. Example: *Min pappa är 72 år. Han föll i trappan för 20 minuter sedan och slog i huvudet. Han blöder lite från pannan och verkar förvirrad. Vi har plåster, kompresser och Alvedon. Vad ska vi göra?*
3. **Keep asking.** It remembers the conversation ("What if it gets worse?", "Explain step 3 more simply"). Press **Ny konversation** when you change subject.
4. **Photos:** press **📷 Foto**. Good light, close up, one thing per photo, and say what you want to know.
5. **Speak instead of typing:** Mac dictation (the 🎤 key, or Fn twice), or the microphone on a phone keyboard.
6. **Check what matters.** AI can be wrong. Open the source under the answer, especially for doses. Never eat a mushroom or plant because the AI says it is edible.
7. **Save power:** the AI uses a lot of power while it answers. Ask few, clear questions, choose 🔋, close other apps.
8. **If it does not work,** the line at the top of the AI page says what is missing: open the **Ollama** app for the AI engine, or the **AnythingLLM** app for the books. The first answer after starting is slower while the model loads.

Life-threatening situations come first: call **112** if any phone works, and use the **Akut** buttons rather than waiting for an AI answer.

### Other ways to use the same AI on the Mac

| Where | Model | When |
|---|---|---|
| **AnythingLLM** app, workspace **Crisis** | Gemma 4 26B through Ollama | Same as 📚. Also shows earlier conversations (including those from the AI page), and lets you drag in your own files |
| **Ollama** app, model **crisis** | Gemma 4 26B with the crisis instructions built in | Same as ⚡. Drag a photo into the chat box to ask about it |
| **Ollama** app, model **crisis-small** | Gemma 4 E4B, same instructions | Same as 🔋 |
| Terminal: `ollama run crisis` | | Type the question; `/bye` to quit |

The instructions the crisis AI follows are in `config/AI-PROMPT.txt`.

## What is in the kit, and why

About 45 GB in all: 14 GB of libraries, 4.5 GB of maps, 1 GB of documents, 27 GB of AI models. It covers what matters first when normal life stops: keeping people alive, then water, warmth, food and information, then getting around.

### 1. Medicine: the most important part

When ambulances are slow or unreachable, the right first-aid steps decide outcomes. Several sources are included because each covers a different angle, and cross-checking matters.

| Library | Why it is here |
|---|---|
| Medical Library | Books written for situations without a doctor: Where There Is No Doctor, Survival and Austere Medicine, Emergency War Surgery, A Book for Midwives, Where There Is No Dentist |
| Military Medicine | Trauma: stopping bleeding, splinting, emergency childbirth, caring for someone over days with few supplies |
| WikiMed and MDWiki | Medical encyclopedias with images: look up symptoms and diseases, recognise rashes, bites, injuries |
| MedlinePlus | Plain-language health and medicine information from the US National Library of Medicine |
| NHS Medicines A to Z | What a medicine is for, side effects, who must not take it |
| CDC Health Information | Infectious disease and outbreaks: how illness spreads, how to protect a household |

### 2. Water, food, shelter, and each kind of emergency

People survive weeks without food but days without water.

| Library | Why it is here |
|---|---|
| Water Treatment Library | Boiling, filtering and chemically treating water |
| Food for Preppers | Storing food and cooking without normal power or ingredients |
| Post Disaster Resource Library | Shelter, sanitation and recovery after a disaster, plus the SAS Survival Handbook |
| Low-tech Magazine | Heating, cooking and living with little or no electricity |
| Ready.gov (US FEMA) | Step-by-step guides the Swedish brochure does not go into: radiation emergencies, nuclear explosion, chemical incidents, explosions, long power outages, winter weather, pandemics. The AI reads these guides and FEMA's "Are You Ready?" handbook |
| A Library of Knots | Shelter, lashing, carrying |

### 3. Information

| Item | Why it is here |
|---|---|
| MCF brochure, Swedish and English | The official Swedish advice: home preparedness, warning signals, what society expects of you |
| Swedish Wikipedia | Every article's opening section: Swedish places, plants, animals, mushrooms, and almost anything else |

### 4. Maps

An offline map of all of Sweden (with parts of Norway, Finland and Denmark inside the same frame) plus a world overview, from OpenStreetMap. Place names are in Swedish. It holds the streets, buildings, paths and house numbers that OpenStreetMap has, and zooms in to single houses.

- **Search** for any town, village, street or address in Sweden, such as *Hornsgatan 50* or *Storgatan 30, Umeå*. If a house number is missing from OpenStreetMap, the pin goes between the neighbouring houses and the map says it is approximate.
- **Nearest** buttons list the closest 🏥 hospitals, 🩺 health centres, 💊 pharmacies, 👮 police, 🚒 fire stations, 🚰 drinking water, 🛒 food shops and ⛽ fuel to the middle of the map.
- **Stockholm** and **Sverige** buttons jump there; the ⦿ button shows where you are (on a phone with GPS).
- **Tap** the map to read exact coordinates, which you can pass on by radio or note down for others.

### 5. More libraries, if you have the space

`config/libraries.txt` lists extras you can switch on by removing the `#` in front of them, then running `bash scripts/download-library.sh`: Swedish Wikipedia in full with images (17 GB), English Wikipedia (13 GB, or 49 GB in full), iFixit repair guides, and Q&A sites for home repair, cars, gardening, cooking, the outdoors and amateur radio. Run `bash scripts/get-documents.sh` and `bash scripts/embed-documents.sh` afterwards if you add libraries with books in them.

## Add your own documents

Put files in the kit's `documents/` folder (contact lists, medication lists, insurance papers, manuals for your generator or water filter), then run `bash scripts/embed-documents.sh`. The AI can then answer from them too. You can also drag files straight into the Crisis workspace in AnythingLLM. Your own documents never leave the Mac and are never part of the repository.

## Folder layout

| Path | Contents |
|---|---|
| `install.sh` | Installs or repairs everything |
| `Start Crisis Kit.command` | Double-click to start everything |
| `config/` | `libraries.txt` (which libraries), `AI-PROMPT.txt` (the AI's instructions), `document-names.json` (book titles) |
| `scripts/` | `share-library.sh` (start), `serve-web.py` (web server, and the bridge from the AI page to Ollama and AnythingLLM), `build-home.py` (start page), the `get-*.sh` download steps, `setup-ai.sh`, `embed-documents.sh`, `extract-documents.py`, `build-map-index.py` (map search) |
| `web/` | The start page, the AI page (`web/ai/`) and the map (`web/map/`) |
| `library/` | Offline libraries (.zim files), downloaded. The Kiwix app can open them too |
| `documents/` | MCF brochure, and `library/` with every book as a PDF, named by title, downloaded |
| `maps/` | Sweden and world map files, downloaded |
| `tools/`, `logs/` | Helper programs and logs |

## Keep it fresh

Libraries do not update themselves. A few times a year, put newer file names from https://download.kiwix.org/zim/ into `config/libraries.txt` and run `bash scripts/download-library.sh`. Re-running is always safe: it skips finished files and resumes partial ones. The start page rebuilds itself from whatever is installed each time you start the kit. `git pull` gets the newest version of the kit itself.

The map search can be rebuilt from fresh OpenStreetMap data with `scripts/build-map-index.py` (needs `brew install osmium-tool` and `maps/osm/sweden-latest.osm.pbf` from download.geofabrik.de).

Once a month, turn off Wi-Fi and check that the start page, a search, the map and the AI all still work.

## Still worth doing by hand

- Install **Organic Maps** on your phone and download Sweden: a second map that runs for days on a power bank.
- Install **Kiwix** on your phone and copy the medical libraries to it.
- Buy a battery or crank radio for P4, and a power bank or power station for the Mac.

## Credits and licence

The kit's own code is under the MIT licence (`LICENSE`). The libraries, maps, brochures and AI models are downloaded from their original sources and keep their own licences: see `CREDITS.md`. Inspired by [Project N.O.M.A.D.](https://github.com/Crosstalk-Solutions/project-nomad).

This kit is not medical advice and does not replace emergency services. In an emergency, call 112.
