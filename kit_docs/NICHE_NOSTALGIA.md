# Niche: childhood nostalgia · familiar faces · tragic endings (template: Final Reel)

Ye file is niche ka poora tareeqa hai: child stars, "gone too soon", "where are they now", celebrity memorial lists,
classic TV / film stars. Template: **`finalreel`** (preview: `templates/finalreel/previews/sheet.jpg`).
Pehli video: *35 Child Actors Who Died Too Soon — How Many Do You Remember?* (`projects/child_stars_died_too_soon/`).

---

## 1. Ek dafa: niche workspace (kit ke main folder se)

```
python niche.py new child-stars --template finalreel --topic "child actors and child stars who died young: childhood nostalgia, classic TV shows and films, their lives and tragic endings"
```

`finalreel` template QC ko **people mode** par set karta hai: us shakhs ki apni tasweeren / portraits allowed;
YouTube thumbnails, memes, collages, kisi aur ki tasweer, interview / talking-head clips, logos, chyrons, watermarks
reject. Phir Claude ko `workspaces\child-stars` folder mein kholein.

## 2. Har video ke liye footage (3 qadam)

1. **Logon ki tasweeren** — ek text file, har line par ek shakhs: `Name | woh kis cheez se mash'hoor hai`
   ```
   River Phoenix | Stand By Me 1986
   Judith Barsi | Land Before Time Ducky voice
   ```
   `python niche.py people child-stars names.txt` → har shakhs ki ~9 tasweeren `pool/images/<naam>__g....jpg`
   (Google Images + Wikimedia; stock / watermark sites block). `SERPER_API_KEY` `api_keys/keys.env` mein ho.
2. **Competitor / reference video ki clips** (agar ho) — video download kar ke:
   ```
   python docu/tools/comp_clips.py "<competitor.mp4>" workspaces/child-stars/pool/clips --names workspaces/child-stars/pool/people.json
   ```
   Ye un ke frame ke **andar** wala box dhoondh kar sirf asal show / film ki clips kaatta hai (bina awaaz), aur har
   clip ka naam us shakhs ke naam par rakhta hai (`river_phoenix__cmp_034_319s.mp4`). Un ke graphics / text bahar.
3. **Nostalgic B-roll** (VHS, CRT TV, projector, Hollywood, rain, candles...):
   ```
   python docu/tools/fetch_online.py --out tmp_broll --query "vhs tape, old crt television static, film projector, hollywood sign, memorial candles, rain on window night" --clips 3 --photos 0 --sources pexels,pixabay
   ```
   phir files ke naam ke aage `broll_` laga kar `pool/clips/` mein daal dein.

Phir **QC**: `python niche.py qc child-stars` (sirf nayi files check hoti hain).

## 3. Video banana (Claude editor)

```
make.bat --yes --title "<title>" --script <script.txt> --audio <vo.mp3> --srt <vo.srt> --until shotlist
```

Shot list ke liye **`projects/child_stars_died_too_soon/build.py` copy karein** — ye data se chalta hai:
- `PEOPLE` table: `(naam, us ki entry ke pehle alfaaz, role / mash'hoor kis se, "1970 — 1993", umar, umar wali line, extras)`
  extras: `memo` (memoriam card ki line) + `memo_at`, `life` (lifeline events), `map` (jagah), `quote`, `note`, `tv=True`
  (purani black & white shows TV frame mein).
- Cold open (pehle ~55 s) haath se: har subtitle line par ek shot (1.5–2 s), `rollcall` "Thirty-five ..." par.
- Outro: `rollcall` ("Thirty-five names"), un ke naam jin se qanoon / foundations bane, aakhri `memoriam`.
- Baqi sab khud: castcard naam par → un ki clips (frame ke andar) / tasweeren → B-roll mood ke hisaab se →
  `ageclock` umar wali line par → `memoriam` jahan kahani sab se bhaari ho.
- Music: `edl.main(music=[...])` — har ~3 minute baad naya somber bed.

`make.bat --resume plan` → **EDIT AUDIT** pass hona chahiye → `--resume render --upload` → final QC dekhein.

## 4. Qawaid (is niche ke)

- **Sach**: har maut, umar, tareekh script ke mutabiq; kisi zinda shakhs ko faut na dikhayein. Jahan paidaish ka saal
  pakka na ho, castcard mein sirf `"DIED 2020"` likhein.
- Borrowed clips: 2–4 s, bina awaaz, **frame ke andar** (`reelframe`) ya TV gate mein, hamesha narration ke saath;
  kabhi full screen nahi. Interview / talking head clips QC khud nikal deta hai.
- Suicide / overdose / qatl: seedha, bina tafseel; B-roll naram (baarish, mom-batti, khaali jhoola), sensational nahi.
- ~25–30 % clips (borrowed + B-roll), ~70 % tasweeren aur graphics.
- Har shakhs ki kam az kam 4 QC-pass tasweeren; kam hon to `niche.py people` dobara chalayein.

## 5. Template ke devices (short)

`castcard` (kaun hai) · `ageclock` (umar) · `memoriam` (aakhri card) · `rollcall` (chehron ki deewar) ·
`lifeline` (zindagi ki timeline) · overlay `reelframe` (frame ke andar clip, render `inset`) · overlay `nameplate`
· saath mein `map`, `quote`, `depth`. Tafseel: `templates/finalreel/README.md`.
