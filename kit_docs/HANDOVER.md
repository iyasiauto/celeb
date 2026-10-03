# HANDOVER — apne PC par is kit ko chalana (Claude ke liye bhi, aap ke liye bhi)

Ye file dono ke liye hai: **aap** iske steps follow karein, aur **Claude** (ya koi bhi AI agent) ise parh
kar poora context samajh le — kya ban chuka hai, kahan rakha hai, aur nayi video kaise banani hai.
Agent ko sirf itna kehna kaafi hai: **"HANDOVER.md aur AGENTS.md parho, phir video banao."**

---

## 1. Ye kit kya hai

Ek mukammal, khud-mukhtar video factory. Script + voiceover + footage dein, ye 1080p30 documentary
video bana deti hai: word-exact editing, template ke apne graphics, maps, sound design, music beds,
YouTube metadata aur chapters. Koi AI-generated picture nahi, koi talking head nahi — sirf aap ki
footage aur free-licence stock.

Engine headless Chromium + FFmpeg par chalta hai, poora offline. AI sirf **optional** hai (shot list
likhwane ya pictures describe karne ke liye); uske baghair bhi sab kaam karta hai.

---

## 2. Pehli dafa setup (PC par, ~10 minute)

1. **Python 3.10+** install karein — windows par "Add python.exe to PATH" tick karna na bhoolein.
2. Zip unzip karein, maslan `D:\DocuKit`.
3. `setup.bat` (Windows) ya `./setup.sh` (Mac/Linux) chalayein — packages, Chromium aur FFmpeg aa jayenge.
4. *(Optional)* `api_keys\keys.example.env` ko copy kar ke `api_keys\keys.env` banayein aur apni keys
   bharein (Pexels, Pixabay, FameSpeak, OpenRouter/OpenLux…). **Ye file git mein kabhi nahi jati aur
   Claude ko ise print nahi karna chahiye.**
5. Test: `python make_video.py --help` chal jaye to sab theek hai.

Agar Frontier folder PC par mojood hai, `FRONTIER_DIR` set kar dein — uske `.env` ki keys khud mil
jayengi aur uske assets (fonts, music, cut-outs) bhi istemal ho jayenge.

---

## 3. Ek nayi video banane ka tareeqa

### Sab se aasan (wizard)

```
python make_video.py
```

Ye khud poochta hai: title → script → voiceover → template → footage. Phir video ban jati hai.

### Ek line mein

```
python make_video.py --yes --title "<title>" --script inputs\script.txt ^
  --audio inputs\vo.mp3 --srt inputs\vo.srt ^
  --template almanac --folder "D:\Footage\MeraData" --upload
```

- `--template` : `documentary` · `almanac` · `paper` · `forensic` · `expedition` · `broadcast`
- footage: `--folder <PC ka folder>` ya `--drive <link>` ya `--niche <naam>` ya `--online "search, search"`
- `--upload` lagayein to aakhir mein gofile link mil jata hai.

### Sab se achha — Claude khud editor bane

Channel ki saari videos is tareeqe se bani hain. Agent ko kehna hai:

1. `python make_video.py --title "..." --script ... --audio ... --template almanac --folder "..." --until shotlist`
2. `docu/VISUAL_SYNC_GUIDE.md`, `TEMPLATES.md` ka us template wala section, aur `projects/<koi example>/build.py`
   parho; `projects/<slug>/data/` (script, words.json, catalog, image picks) aur `media/<slug>/cat/` ki
   contact sheets dekho.
3. `projects/<slug>/build.py` ki shot list khud likho — har jumle par wahi shot jo us jumle ko dikhaye.
4. `python make_video.py --title "..." --yes --resume plan --until stills` → har WARN theek karo, stills dekho.
5. `python make_video.py --title "..." --yes --resume render --upload`

---

## 4. Ab tak kya ban chuka hai (channel ki history)

| # | Video | Template | Project folder |
|---|---|---|---|
| 1–2 | Noah's Ark (4,300 years / 100 % confirmed) | paper, forensic | `projects/noahs_ark`, `projects/noahs_ark_100` |
| 3–4 | Noah's Ark (myth or reality / breaking) | expedition, broadcast | `projects/noahs_ark_myth`, `projects/noahs_ark_breaking` |
| 5–6 | Hasidic (10 kids / benefits cut) | documentary | `projects/hasidic_10_kids`, `projects/hasidic_benefits_cut` |
| 7 | Why Thousands of Amish Are Leaving Their 300-Year Homeland (17 min) | heritage almanac, **pehla edition** | `projects/amish_leaving` |
| 8 | Pennsylvania Has 95,000 Amish — So Why Does Wisconsin Have MORE Settlements? (20:35) | heritage almanac, **updated edition** | `projects/amish_two_states` |

Har project folder mein uski poori shot list (`build.py`), uska data (`data/`) aur YouTube metadata
(`youtube_metadata.txt`) mojood hai. **Nayi video likhte waqt sab se milta-julta project kholein aur
usi andaz mein likhein** — yahi is channel ka style guide hai.

---

## 5. Heritage almanac ka updated edition (video 8 mein bana)

Template purane se badla gaya hai, naya template nahi banaya gaya. Ab:

- Headings: **engraved caps (Cinzel)** letterpress plate aur "PLATE IV" stamp ke saath, chalti footage par.
- Numbers: **Playfair (didone)**, body **EB Garamond**, notes **surveyor ki pencil (Patrick Hand)**.
- Colours: **slate ink, ochre, oxblood, verdigris** — oatmeal paper par (pehle barn red / field green / wheat thay).
- Cards: **ledger slip** (punched holes, double keyline, ochre band) — pehle quilt frame tha.
- Map: **plat map** — township grid, square section markers, slate cartouches, aur dots jinka size value
  ke hisab se rakha ja sakta hai.
- Paanch nayi scenes: `gzversus`, `gzgiants`, `gzdivide`, `gzindex`, `gzdelta` (detail `TEMPLATES.md` §2).
- Purana look khatam nahi hua: `theme="almanac_v1"` likhne se wahi warm/slab wala version wapas aa jata hai.

---

## 6. Data library (ek subject ka footage dobara dobara use karna)

`docu/tools/pool.py` ek folder ko "pool" bana deta hai — ek hi subject ka saara footage ek jagah, har
file ke page, licence aur tags ke saath. Phir har nayi video par wahi pool kaam aata hai.

```
python docu/tools/fetch_online.py --out tmp_new --query "wisconsin dairy farm, amish buggy snow" --clips 3 --photos 4
python docu/tools/pool.py merge  "D:\Footage\Amish"  tmp_new        # nayi files pool mein
python docu/tools/pool.py build  "D:\Footage\Amish"  --name "Amish" # library.json, tags.json, CREDITS.md, README.md
python docu/tools/pool.py sheets "D:\Footage\Amish"  sheets_out     # contact sheets (dekhne ke liye)
```

Phir ek dafa niche register kar dein, uske baad sirf naam kaafi hai:

```
python docu/studio/studio.py niche-add --name "Amish" --folder "D:\Footage\Amish" ^
   --clips clips --images images --tags "D:\Footage\Amish\tags.json" --clip-share 45 --style almanac
python make_video.py ... --niche amish
```

**Cloud session mein jo Amish pool bana tha (151 clips + 222 pictures) wo us container mein tha, is zip
mein nahi** — zip bara ho jata. Apne PC par ya to apna footage folder dein, ya `fetch_online.py` se
dobara mangwa lein, ya mujhse us pool ka alag link maang lein.

---

## 7. Qawaid (inhe Claude bhi follow kare)

- **Keys** sirf `api_keys/keys.env` mein. Kabhi print na karein, kabhi commit na karein.
- Sirf user ki footage + free libraries (Pexels, Pixabay, Wikimedia). **Koi AI-generated picture nahi**,
  koi talking head nahi, koi watermark nahi — aisi file ho to `media/<slug>/src/` se delete kar ke
  `--resume catalog` chala dein.
- Music hamesha awaaz ke neeche (default already set hai), final −14 LUFS.
- Video 1 GB se kam ho (zaroorat par 2-pass re-encode khud ho jata hai), gofile link md5 ke saath.
- Koi step fail ho to log parhein, theek karein, aur `--resume <stage>` se wahin se chalayein — shuru se nahi.
  Stages: `footage catalog voice timing shotlist plan prep stills render mix final deliver metadata`.
- Poori video render hone mein 1–2 ghante lagte hain. Background mein chalayein aur log dekhte rahein.

---

## 8. Claude ko dene ke liye pehla message (copy-paste)

```
Is folder mein video banane ki kit hai. Pehle HANDOVER.md aur AGENTS.md parho.
Phir mujh se ek hi message mein poocho: title, script, voiceover (MP3+SRT ya FameSpeak voice ID),
template (1-6), aur footage kahan hai (PC folder / Drive link / niche / online).
Uske baad khud editor ban kar shot list likho (--until shotlist, phir --resume plan),
stills check karo, render karo aur mujhe final file aur gofile link do.
```
