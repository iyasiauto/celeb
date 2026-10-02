# The 6 templates

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
![sheet](docu/templates/previews/sheet_almanac.jpg)

- **Best for:** rural life, traditions, migrations, land and family stories. Warm and slow, footage zyada.
- **Look:**
  - Video **opens on moving footage** (kabhi still nahi).
  - Slab-serif chapter headings **rise over the moving clip**, with a stitched badge (I, II, III…).
  - Seed-packet place tags, quilt-frame key-point cards.
  - Charts drawn on cream paper.
  - Cream survey map: red target markers, ink-keyline name tags, inked routes with arrowheads.
  - Colours: barn red, field green, wheat, denim.
- **Signature scenes:**
  - `almhead` (heading overlay on a clip)
  - `almtag`
  - `almcard`
  - `almstat`
  - `almgrowth` (line across years; each point appears on its words)
  - `almsplit` (a farm fenced into equal strips)
  - `almdots` (generations as dots)
  - `almshare` (one bar, shares)
  - `almbars`
  - `almdistrict` (ring of houses around a centre)
- **Settings:** `theme="almanac", grade="almanac", grain 4, xfade 0.5, sfx_style="calm"`, about 45–50 % clips.
- **Example:** *Why Thousands of Amish Are Leaving Their 300-Year Homeland*: `projects/amish_leaving/`
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
