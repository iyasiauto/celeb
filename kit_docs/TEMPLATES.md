# The templates

Kit ke saath 8 templates aate hain (neeche; 7th: **Final Reel** — `templates/finalreel/README.md`, 8th: **The Record** — `templates/record/README.md`). Ye sab **registry** mein hain: `templates/<id>/template.json` har
template ki playbook hai (devices aur kitne chahiye, audit limits, rules, previews, examples) aur
`styles/<id>/` un ke variations. Naya template / style = naya folder (`python docu/registry.py new-template` /
`new-style`, guide: `templates/README.md`, `styles/README.md`). Agent har video se pehle
`python docu/registry.py show <id> --minutes <length>` parhta hai, aur edit audit wahi minimums enforce karta hai.
**Har engine device har template mein chalta hai** (`templates/devices.json`) - playbook minimum hai, limit nahi.

Har template ek **theme** (fonts, colours, map ka style), ek **grade** (photo aur clip ka colour), aur
**scene types** ka set hai. Engine sab ka ek hi hai: `docu/`. Kisi template ka naam `--template <id>` ya
wizard ke number se chunein. Har template ki full preview sheet `docu/templates/previews/sheet_<id>.jpg` mein hai.
Har scene ki alag preview aur options `docu/templates/README.md` §6 mein hain.

Shot list (`build.py`) mein sirf `edl.setup(theme=..., grade=...)` badalne se look badal jaata hai, magar har
template ke apne "signature" scenes hain. Wizard aur Docu Studio un ko khud chunte hain (`docu/studio/shots.py`).

---

## 1 · Calm documentary — `documentary`
![sheet](docu/templates/previews/sheet_documentary.jpg)

- **Best for:** communities, economics, culture. Viewer ko samajh aaye, chakachaundh na ho.
- **Look:** slow photographs (Ken Burns), 0.6 s soft dissolves, serif chapter cards ("Chapter 3"), location
  caption with a thin gold rule, name lower thirds, one- to three-line text cards over darkened photos.
- **Signature scenes:**
  - `doctitle` (chapter)
  - `textcard`
  - `bars` (gentle bar chart)
  - `ledgerlist` (household ledger that grows)
  - `sizechart`
  - overlays `place` and `doclower`
  - maps with one route
- **Settings:** `theme="documentary", grade="doc", grain 1.5, xfade 0.6, sfx_style="calm"`, about 30 % clips.
- **Variety:** `vary="auto"` gives every video its own accent colour, fonts, grade, chapter-number style and
  music order, and avoids pictures already used in earlier videos.
- **Examples:**
  - *How Do Hasidic Jews Afford 10 Kids Without Jobs*: `projects/hasidic_10_kids/`
  - *What Happens If the Government Cuts Hasidic Benefits*: `projects/hasidic_benefits_cut/`
- **Starter:** `docu/templates/starter_documentary/build.py`

## 2 · Heritage almanac — `almanac`
![sheet](docu/templates/previews/sheet_almanac2.jpg)

- **Best for:** rural life, traditions, migrations, land and family stories, aur numbers wali
  comparison videos (do states, do daur, chhote aur bare ka farq). Slow, calm, footage zyada.
- **Look** (ye updated edition hai — purana warm/slab wala version `almanac_v1` ke naam se mojood hai):
  - Video **opens on moving footage** (kabhi still nahi).
  - Chapter heading **engraved caps** (Cinzel) mein, ek letterpress plate aur "PLATE IV" stamp ke saath,
    chalti footage par — letter-spacing band hoti hai, hairlines beech se khulti hain.
  - **Didone figures** (Playfair) bare numbers ke liye, **EB Garamond** body, aur **surveyor ki pencil**
    (Patrick Hand) notes ke liye.
  - Key points **ledger slip** par: punched holes, double keyline, ochre band.
  - **Plat map:** township grid, square section markers, slate cartouche labels, aur dots jinka size
    badla ja sakta hai (ek dot 40 logon ka, dusra 44,765 ka).
  - Colours: slate ink, ochre, oxblood, verdigris — oatmeal paper par.
- **Signature scenes:**
  - `gzhead` (heading overlay on a clip) · `gztag` (place cartouche)
  - `gzcard` (ledger-slip key point) · `gzstat` (one stamped figure)
  - `gzversus` — do cheezein row by row compare (population / settlements / districts), har value
    apne lafz par count hoti hai, aagay wali side tinted
  - `gzgiants` — ek bara circle (value ke hisab se) aur barabar mein chhote dots ka field
  - `gzdivide` — ek cell boundary ke andar do, teen, dus mein divide hota hua
  - `gzindex` — gazetteer index rows: naam · dotted leader · figure
  - `gzdelta` — 2015 → 2025, arrow ke saath, farq stamp kiya hua
  - aur almanac ke paper charts isi naye palette mein: `almgrowth`, `almsplit`, `almdots`,
    `almshare`, `almbars`, `almdistrict`
- **Settings:** `theme="almanac", grain 3.5, xfade 0.55, sfx_style="calm"` (grade khud `almanac2` ban
  jata hai), about 35–50 % clips.
- **Examples:**
  - *Pennsylvania Has 95,000 Amish — So Why Does Wisconsin Have MORE Settlements?*: `projects/amish_two_states/`
    (updated edition — 194 shots, saari nayi scenes)
  - *Why Thousands of Amish Are Leaving Their 300-Year Homeland*: `projects/amish_leaving/`
    (pehla edition, `theme="almanac_v1"` se waisa hi render hoga)
- **Starter:** `docu/templates/starter_almanac/build.py`

## 3 · Paper / Vox explainer — `paper`
![sheet](docu/templates/previews/sheet_paper.jpg)

- **Best for:** explainers, myths, history, "how it works".
- **Look:** a paper tabletop. Photos as prints, cut-outs with white keylines, typed strips, rubber stamps,
  newspaper pages, sticky notes, ledger arithmetic; things drop, slide and stamp in.
- **Signature scenes:**
  - `collage` (with photo, cut-out, strip, stamp, note and title items)
  - `newspaper`
  - `headlines`
  - `baskets` (known / claimed / unknown folders)
  - `chapter`
  - `depth` pop
  - `spotlight`
  - `words` slam
  - `stat`
  - `quote`
  - `ledger`
  - `timeline`
- **Settings:** `theme="paper", grade="doc", grain 4–5`, hard cuts, full sound design, about 25 % clips.
- **Example:** *Noah's Ark Confirmed After 4,300 Years?*: `projects/noahs_ark/`
- **Starter:** `docu/templates/starter/build.py`

## 4 · Forensic lab report — `forensic`
![sheet](docu/templates/previews/sheet_forensic.jpg)

- **Best for:** "is this claim true?", evidence checks, debunks.
- **Look:** a lab report / case file. Graph paper, stencil stamps, cyan and amber, x-ray scans.
- **Signature scenes:**
  - `filter` (OBSERVED / CLAIMED / CONFIRMED sorting)
  - `gauge` (certainty ring 100 % → 0 %)
  - `network` (everything traces back to one source)
  - `valley`
  - `cells`
  - scan items
- **Settings:** `theme="forensic", grade="cool", grain 2`.
- **Example:** *Noah's Ark "100 % Confirmed"?*: `projects/noahs_ark_100/`

## 5 · Expedition & courtroom — `expedition`
![sheet](docu/templates/previews/sheet_expedition.jpg)

- **Best for:** hunts, mysteries, "myth or reality", a verdict at the end.
- **Look:** an explorer's field journal and a courtroom. Ruled journal pages, leather desk, antique parchment
  map, brass and oxblood, evidence tags EXHIBIT A–D.
- **Signature scenes:**
  - `scales` (scales of justice tipping)
  - `scoreboard` (split-flap)
  - `verdict` (REALITY / MYTH)
  - tag items
  - parchment map routes
- **Settings:** `theme="expedition", grade="warmsepia", grain 2`.
- **Example:** *Myth or Reality? Hunting for the REAL Noah's Ark*: `projects/noahs_ark_myth/`

## 6 · Breaking-news broadcast — `broadcast`
![sheet](docu/templates/previews/sheet_broadcast.jpg)

- **Best for:** news-style updates, "BREAKING", fast reveals.
- **Look:** a news desk. LIVE bug and a crawling ticker, BREAKING NEWS slab, lower-third bars, navy studio,
  signal red and alert yellow, heavy geometric sans type.
- **Signature scenes:**
  - `breaking`
  - `borehole` (cross-section)
  - `factcheck` meters
  - `echo` (headline wall → one source)
  - `columns`
  - `videowall`
  - `newslist`
  - `segment` bumpers
  - overlays `ticker`, `bug`, `newslower`
- **Settings:** `theme="broadcast", grade="broadcast", grain 1.5`.
- **Example:** *BREAKING: They Drilled Into Noah's Ark*: `projects/noahs_ark_breaking/`
- **Starter:** `docu/templates/starter_broadcast/build.py`

---

## Apna template banana

`styles/_example/` ko copy karke `styles/<naam>/` banayein. `style.json` mein naam, base theme, blurb, rules aur
example likhein. Ye wizard aur Docu Studio dono mein khud aa jaata hai (detail: `styles/README.md`).
Bilkul naya look chahiye (naye scenes) to `docu/scenes_almanac.js` ek mukammal misaal hai; tareeqa
`docu/templates/README.md` §13 mein hai.

## Sab templates mein common

- **Word-exact timing:** har shot apne lafz par shuru hota hai. `"@words"` se kisi element ka time us lafz par
  rakhte hain.
- **No repeats:** pichli videos mein use hui pictures aur clips `assets_used.json` se pehchaan kar avoid hoti hain.
- **Sound:** synthesised SFX, music beds per act, music voice ke neeche ducked, −14 LUFS.
- **Delivery:** 1 GB se kam (zaroorat par 2-pass re-encode), gofile link with md5 check, YouTube metadata with chapters.


## 7 · Final Reel — `finalreel`
![sheet](templates/finalreel/previews/sheet.jpg)

- **Best for:** childhood nostalgia, child stars, celebrities, "gone too soon", memorial lists.
- **Look:** a film-archive memorial — charcoal and ivory, muted gold, one crimson for the ending; Playfair names,
  condensed caps, typewriter dates; portraits in ivory film frames; borrowed clips play inside the frame.
- **Signature scenes:** `castcard`, `ageclock`, `memoriam`, `rollcall`, `lifeline`; overlays `reelframe`, `nameplate`.
- **Settings:** `template="finalreel"` (grade `reel`, grain 3, xfade 0.6, calm sound), ~25–30 % clips, QC people mode.
- **Example:** *35 Child Actors Who Died Too Soon*: `projects/child_stars_died_too_soon/` · niche guide: `NICHE_NOSTALGIA.md`.


## 8 · The Record — `record`
![sheet](templates/record/previews/sheet.jpg)

- **Best for:** investigative documentaries — closed communities and institutions, cover-ups, silence and pressure,
  court cases, rulings, how a system protects itself.
- **Look:** the case assembled from the record — blue-black ink ground with a ledger grid, bone paper pages, steel
  labels, one sodium-amber signal; Crimson Pro statements, condensed caps, Kode Mono for files, Hebrew in Frank Ruhl.
- **Signature scenes:** `docket` (FILE 03 / 10), `transcript` (line-numbered ruling, marked words), `lexicon`
  (Hebrew term), `tally`, `counts`, `chain` (gate, delay clock, block), `redacted`, `wall` (posters), `docketline`,
  `ripple`, `ballot`; overlays `casebox` (evidence viewer for every stock clip), `source`, `place`.
- **Settings:** `template="record"` (grade `record`, grain 1.6, xfade 0.4, full sound under the voice), 30–38 % clips,
  every clip under 5 s, QC faceless mode.
- **Example:** *Why 20,000 Hasidic Jews Were Told To Stay Silent About Crime?*: `projects/hasidic_mesirah/`.
