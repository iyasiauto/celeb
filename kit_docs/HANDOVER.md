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

## 3. Kit v2 mein kya naya hai (zaroor parhein)

Ye kit **kisi bhi niche** ke liye hai (true crime, space, history, religion, travel, Amish, Hasidic…).
Niche sirf ek naam + topic + footage pool hai; look template se aata hai. Pichli kit mein jo masle thay
(agent templates ko sirf upar upar se use karta tha, devices/maps/textures/VHS/SFX nahi lagata tha,
talking heads aur logo wali clips aa jati thin, niches mix ho jate thay) un ke liye ab **teen gate** hain
jo agent bypass nahi kar sakta:

| Gate | Kya rokta hai | Kab chalta hai |
|---|---|---|
| **QC** (OpenLux · Gemini 2.5 Flash Lite) | talking head, influencer / face-cam, posed face, eye contact, stock watermark, beech ka logo, kisi aur ke captions, topic se bahar footage. **Corner logo** wali clip crop ho kar zoom/effect ke saath hamari ban jati hai | footage aate hi (`qc.json`); har nayi file sirf ek dafa check hoti hai. Jo clip/picture QC mein nahi ya reject hai, engine use **chalne hi nahi deta** |
| **Edit audit** | "slideshow" video: template ke devices kam, graphics kam, lambe plain hisse, jagah ka naam aaye aur map na ho, number bola jaye aur dikhaya na jaye, repeat shots, chapters na hon | `plan` par; koi **FAIL** ho to **render block** |
| **Final QC** | jo phir bhi reh gaya: har shot ko us par boli ja rahi line aur niche ke topic ke against dekhta hai | `final` ke baad; flagged shots `final_qc.md` + `final_qc_flags.jpg` mein |

Saath mein **finishing layers khud lagti hain** (template ke hisab se, `docu/asset_mix.py`): footage par grain /
paper / scan-line texture, opening aur har chapter heading par dust / light-leak / VHS overlay, aur jis shot
ko editor `archive=True` kare us par vintage TV frame.

---

## 4. Har niche ka alag workspace (niches kabhi mix nahi hote)

```
python niche.py new true-crime --template forensic --pool "D:\Footage\Crime" --topic "unsolved crimes in the US"
python niche.py new space --template documentary --drive "<drive folder link>" --topic "space missions"
python niche.py qc true-crime          # poore pool ka vision QC (pehli dafa; baad mein sirf nayi files)
python niche.py list
```

Har workspace (`workspaces/<niche>/`) ka apna pool, apna `qc.json`, apne projects, apni renders, aur apni
`CLAUDE.md` hoti hai. **Claude ko us workspace folder mein kholein** — wo sirf us niche ko dekhega. Video:

```
cd workspaces\true-crime
make.bat --yes --title "<title>" --script <script.txt> --audio <vo.mp3> --srt <vo.srt> --until shotlist
```

Har video `projects/<slug>/project.json` mein apna template, style, niche aur topic **pin** kar leti hai; koi
doosra template maange to wo ruk jati hai. Ek video = ek template = ek niche.

---

## 5. Naya template ya style add karna (folder daalo, ho gaya)

```
python docu/registry.py list                                   # sab templates + styles
python docu/registry.py show almanac --minutes 20              # playbook: devices, kitne chahiye, previews, examples
python docu/registry.py new-template cold-case --from forensic # kisi template ki copy se naya
python docu/registry.py new-template my-look --from _example   # bilkul naya look: apni scene JS + fonts + rang
python docu/registry.py new-style forensic-red --template forensic
python docu/registry.py check
```

- `templates/<id>/template.json` — devices (har ek ka `min_per_10min`), audit limits, rules, previews,
  examples; apna look `theme_def` (fonts / colours / grounds) mein, apni scenes `scene_files` (JS) mein.
  **Engine mein koi edit nahi** — folder daalte hi list mein aa jata hai.
- `styles/<id>/style.json` — kisi template ke upar palette / fonts / pacing / device minimums / `rules.md`
  (Frontier ke styles jaisa).
- `datadoc` template ke liye apne PC wali `scenes_datadoc.js` ko `docu/` mein rakh dein (fonts kit mein hain).

---

## 6. Ek nayi video banane ka tareeqa

### Sab se achha — Claude khud editor bane (channel ki saari videos aise bani hain)

1. Workspace mein: `make.bat --yes --title "..." --script ... --audio ... --srt ... --until shotlist`
   (kit root se: `python make_video.py ... --template <id> --folder "<footage>" --topic "<topic>"`)
2. `python docu/registry.py show <template> --minutes <length>` — preview sheet aur har device ka preview
   dekho, ek worked example (`projects/<example>/build.py`) **poora** parho, `docu/VISUAL_SYNC_GUIDE.md` parho.
3. `projects/<slug>/build.py` ki shot list likho: har jumle par wahi shot jo usay dikhaye; har jagah ka naam →
   map (`python docu/tools/places.py find "<jagah>"`), har number → number device, quote → `quote`,
   purani / "us zamane" wali shots par `archive=True`.
4. `make.bat --title "..." --yes --resume plan --until stills` → **EDIT AUDIT** ke saare FAIL theek karo, stills dekho.
5. `make.bat --title "..." --yes --resume render --upload` → final QC dekho, flagged shots badlo,
   `python build.py render s012 && python build.py final`.

### Ek line mein (AI editor khud likhe)

```
python make_video.py --yes --title "<title>" --script inputs\script.txt --audio inputs\vo.mp3 --srt inputs\vo.srt ^
  --template almanac --folder "D:\Footage\MeraData" --topic "<niche ka topic>" --upload
```

---

## 7. Ab tak kya ban chuka hai (channel ki history)

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

## 8. Heritage almanac ka updated edition (video 8 mein bana)

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

## 9. Data library (ek subject ka footage dobara dobara use karna)

`docu/tools/pool.py` ek folder ko "pool" bana deta hai — ek hi subject ka saara footage ek jagah, har
file ke page, licence aur tags ke saath. Phir har nayi video par wahi pool kaam aata hai.

```
python docu/tools/fetch_online.py --out tmp_new --query "wisconsin dairy farm, amish buggy snow" --clips 3 --photos 4
python docu/tools/pool.py merge  "D:\Footage\Amish"  tmp_new        # nayi files pool mein
python docu/tools/pool.py build  "D:\Footage\Amish"  --name "Amish" # library.json, tags.json, CREDITS.md, README.md
python docu/tools/pool.py sheets "D:\Footage\Amish"  sheets_out     # contact sheets (dekhne ke liye)
```

Phir us pool ko ek niche workspace bana dein (section 4):

```
python niche.py new amish --template almanac --pool "D:\\Footage\\Amish" --topic "Amish life and settlements"
python niche.py qc amish
```

Amish pool (151 clips + 222 pictures, `qc.json` ke saath) alag zips mein diya gaya tha; unzip kar ke `--pool`
mein us folder ka path dein — QC dobara nahi chalega, `qc.json` saath hai.

---

## 10. Qawaid (inhe Claude bhi follow kare)

- **Keys** sirf `api_keys/keys.env` mein. Kabhi print na karein, kabhi commit na karein.
- Sirf user ki footage + free libraries (Pexels, Pixabay, Wikimedia). **Koi AI-generated picture nahi.**
- **Strict:** koi official clip channel logo ke saath nahi, koi talking head nahi, kisi influencer ka chehra
  (clip ya picture) nahi, koi watermark nahi. Corner watermark wali clip crop + effect ke saath hi chalti hai.
  QC (OpenLux key `api_keys/keys.env` mein) ye khud karta hai; `DOCU_SKIP_QC=1` / `DOCU_AUDIT=warn` sirf
  user ke kehne par.
- Music hamesha awaaz ke neeche (default already set hai), final −14 LUFS.
- Video 1 GB se kam ho (zaroorat par 2-pass re-encode khud ho jata hai), gofile link md5 ke saath.
- Koi step fail ho to log parhein, theek karein, aur `--resume <stage>` se wahin se chalayein — shuru se nahi.
  Stages: `footage catalog voice timing shotlist plan prep stills render mix final deliver metadata`.
- Poori video render hone mein 1–2 ghante lagte hain. Background mein chalayein aur log dekhte rahein.

---

## 11. Claude ko dene ke liye pehla message (copy-paste)

```
Is folder mein video banane ki kit hai. Pehle kit_docs/HANDOVER.md aur kit_docs/AGENTS.md parho.
Phir mujh se ek hi message mein poocho: title, script, voiceover (MP3+SRT ya FameSpeak voice ID),
template / style (docu/registry.py list), aur footage kahan hai (workspace pool / PC folder / Drive / online).
Shot list likhne se pehle `docu/registry.py show <template>` chalao, previews dekho, ek example poora parho.
Khud editor ban kar shot list likho, EDIT AUDIT ke saare FAIL theek karo, stills check karo,
render karo, final QC dekho aur mujhe final file, audit score aur gofile link do.
```
