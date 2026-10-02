# Docu Templates Kit · START HERE

Is kit se aap kisi bhi computer par (Windows / Mac / Linux) faceless documentary video bana sakte hain.
Karna sirf ye hai: **template chuno → footage ka folder ya Drive link do (ya online se mangwao) → video ban jati hai.**

Kit mein ye 6 templates hain (detail: [TEMPLATES.md](TEMPLATES.md)):

| # | Template | Kab use karein |
|---|---|---|
| 1 | **Calm documentary** (`documentary`) | communities, economics, culture; slow, samajhne wali video |
| 2 | **Heritage almanac** (`almanac`) | gaon / farm / roayat / migration ki kahaniyan; warm, slow, footage zyada |
| 3 | **Paper / Vox explainer** (`paper`) | explainers, myths, history; paper collage aur cut-outs |
| 4 | **Forensic lab report** (`forensic`) | "kya ye sach hai?" claims ki jaanch, evidence |
| 5 | **Expedition & courtroom** (`expedition`) | khoj, mysteries, faisla / verdict wali videos |
| 6 | **Breaking-news broadcast** (`broadcast`) | news-style, tez, LIVE ticker aur headlines |

---

## 1. Ek dafa setup (10 minute)

1. **Python 3.10+** install karein: <https://www.python.org/downloads/>
   (Windows par install karte waqt **"Add python.exe to PATH"** zaroor tick karein.)
2. Zip ko kisi folder mein unzip karein, maslan `D:\DocuKit`.
3. Setup chalayein:
   - **Windows:** `setup.bat` par double-click.
   - **Mac / Linux:** terminal mein `./setup.sh`.

   Ye Python packages, Chromium (renderer) aur FFmpeg install kar deta hai.
4. *(Optional)* `api_keys\keys.example.env` ko copy karke `api_keys\keys.env` banayein aur jo keys aap ke paas
   hain wo bharein:
   - online footage ke liye Pexels / Pixabay
   - AI shot list ke liye OpenRouter / OpenLux / Claude
   - FameSpeak voice
   - gofile

   Koi key na ho to bhi kit chalta hai: offline shot list aur aap ki apni footage use hoti hai.
   Agar aap Frontier use karte hain to `FRONTIER_DIR` set kar dein; us ki `.env` ki keys bhi khud mil jaati hain.

## 2. Video banana

- **Windows:** `run.bat` par double-click.
- **Mac / Linux:** `./run.sh` (ya `python make_video.py`).

Wizard ye cheezein poochega:

1. **Title** aur **script (.txt)**.
2. **Voiceover:** aap ki MP3 (+ SRT ho to behtar, warna Whisper khud timing nikal leta hai), ya FameSpeak voice ID.
3. **Template:** 1–6 mein se number.
4. **Footage kahan hai:**
   - `1` aap ke PC ka folder. Videos aur pictures, sub-folders bhi chalenge. Files copy nahi hoti, link hoti hain.
   - `2` Google Drive folder link ("Anyone with the link" par share hona chahiye).
   - `3` pehle se bani niche (jaise `hasidic`, `noah`; ye Drive se download hoti hain).
   - `4` kuch nahi. Online se mangwao: Pexels / Pixabay (keys chahiye), Wikimedia Commons (free), aur
     Google Images (optional; licence pata nahi hota, har picture khud check karein).

   Folder ya Drive ke saath bhi "extra footage online" maang sakte hain.

Phir sab khud hota hai:

```
footage → catalog (contact sheets + descriptions) → voice → word timing → shot list → plan check
→ stills → render → sound mix → final MP4 → size < 1 GB (+ gofile link) → YouTube metadata
```

Result yahan milta hai:

- `media/out/<Title>.mp4` aur `.srt`
- `projects/<title>/build.py`: poori shot list. Ise edit karke koi bhi shot badal sakte hain.
- `projects/<title>/youtube_metadata.txt`

### Ek line mein (bina sawalon ke)

```bash
python make_video.py --yes --title "My Video" --script script.txt --audio vo.mp3 --srt vo.srt \
    --template almanac --folder "D:/Footage/Amish" --online "amish buggy, lancaster farm" --upload
```

Baqi options:

| Option | Kaam |
|---|---|
| `--drive <link>` | Google Drive folder se footage |
| `--niche hasidic` | pehle se bani niche |
| `--online auto` | script se searches khud chunna |
| `--sources pexels,pixabay,wikimedia,google` | online sources chunna |
| `--clip-share 40` | % footage clips; baqi pictures aur graphics |
| `--ai none` | hamesha offline rules se shot list |
| `--famespeak-voice <id>` | FameSpeak se voiceover |
| `--resume render` | kisi stage se dobara (`shotlist`, `stills`, `render`, `final`, …) |

## 3. Shot list behtar banana (optional)

- **AI editor:** `api_keys/keys.env` mein `OPENROUTER_API_KEY` (ya OpenLux / Claude / Claude Code CLI) daal dein.
  Shot list AI likhega, [VISUAL_SYNC_GUIDE](docu/VISUAL_SYNC_GUIDE.md) ke tareeqe se: har jumle par sahi picture,
  maps, cards.
- **AI vision** (`OPENLUX_API_KEY`): catalog mein har clip aur picture ki description banata hai. Is se picture
  choice bohat accurate ho jaati hai. Stills ki visual QA bhi karta hai.
- **Bina AI:** offline rules file aur folder ke naamon se match karte hain. Is liye folders ke naam saaf rakhein:
  `buggy/`, `farm aerial/`, `school/`.
- Hath se shot list likhna ho to: [docu/templates/README.md](docu/templates/README.md) aur
  har template ka `docu/templates/starter_*/build.py`.

## 4. Desktop app (optional)

Yehi kaam ek app mein bhi hota hai: **Docu Studio** (Windows zip alag diya gaya hai; source `studio/` folder mein).
Wahan template picker, niche manager, AI settings aur live progress milte hain.

## 5. Masle aur hal

| Masla | Hal |
|---|---|
| `python` nahi milta | Python dobara install karein, "Add to PATH" tick karke |
| Chromium / FFmpeg error | `setup.bat` dobara chalayein |
| Footage kam hai | `--online "..."` se mazeed mangwayein, ya `--clip-share` kam karein |
| Galat picture kisi line par | `projects/<title>/build.py` mein us line ka shot badlein, phir `--resume render` |
| Video 1 GB se bari | deliver step khud chhota karta hai (`--limit-gb`) |
| Kisi stage par ruk gaya | error message dekhein, theek karein, phir `--resume <stage>` |

Detail: [TEMPLATES.md](TEMPLATES.md) · [DATA_SOURCES.md](DATA_SOURCES.md) · [docu/templates/README.md](docu/templates/README.md)
(har scene ka reference) · [docu/INTEGRATION.md](docu/INTEGRATION.md) (apni pipeline mein jodna).
