# Visual sync guide: the right clip and picture on the right word

How every video in this channel matches pictures to narration, written so it works for **any niche and
any style** (documentary, true crime, history, science, biography, news, explainer).

> **Roman Urdu mein khulasa:** Sync do alag kaam hain. **(1) KAB**: har lafz ka waqt voiceover se nikalta
> hai (SRT ya Whisper), aur har scene script ke asli jumle par "cue" hota hai, is liye cut hamesha usi
> lafz par girta hai. Ye kaam machine karti hai aur 100% exact hai. **(2) KYA**: har clip aur tasveer
> ko pehle dekh kar ek line mein likha jata hai ke us mein kya hai. Phir script ke har jumle ke liye poocha
> jata hai "narrator is waqt kis cheez ki taraf ishara kar raha hai?", aur wahi cheez dikhayi jati hai.
> Ye editorial faisla hai, aur neeche ke rules is ko har baar sahi rakhte hain.

---

## 1. Two separate problems

| | Question | Who solves it | Accuracy |
|---|---|---|---|
| **WHEN** | at which moment does the picture change, and when does a label or number appear? | the engine: word timestamps + script alignment | exact to the spoken word (±0.1 s) |
| **WHAT** | which clip or picture belongs to this sentence? | the editor (Claude or you), from a written catalog | as good as the catalog and the rules below |

Most "auto video" pipelines mix these up: they pick visuals by keyword *and* place them on a fixed
timer. Here timing is never guessed, and choice is never automatic without review.

---

## 2. WHEN: timing that can't drift

### 2.1 Word timestamps
- **SRT available** (from your TTS or editor): `tools/srt2words.py voiceover.srt data/words.json`.
  Each subtitle's time span is shared across its words by word length. It's instant and accurate
  for short cues.
- **No SRT:** `tools/transcribe.py vo.mp3 data/words.json` (faster-whisper, word timestamps, ~2 min
  per 15 min of speech on CPU).

### 2.2 Script alignment (`timing.py`)
The script as written is aligned to the words that were heard: both are normalised to lowercase
letters and digits, then matched with a sequence matcher. Words the recogniser got wrong (names,
foreign words) take their time from their matched neighbours. `plan` prints the result as
`alignment 99%`. Below ~95 %, the script and the recording differ; fix `script.txt`.

### 2.3 Cues are phrases, not seconds
```python
at("A volunteer ambulance is parked at the corner", cl(509))
```
- The scene starts **0.12 s before** the first word of the phrase, so the picture arrives just as the
  word does. The scene lasts until the next cue.
- Cues are searched **forward** from the previous one, so a phrase repeated later in the script is
  still found in the right place.
- Pick phrases of 4–8 words that appear once. `plan` names any cue it can't find.
- Re-recorded voiceover? Regenerate `words.json`; the shot list doesn't change.

### 2.4 Inside a scene: `"@phrase"`
Any element can wait for its own word:
```python
ledger("What a real cut looks like", [
    ("Lower a threshold", "", 0.1),                 # seconds from the scene start
    ("Tighten a test", "", "@Tighten a test"),      # appears exactly on those words
    ("Cap a credit", "", "@Cap a credit")])
```
Numbers count up on the word, pins drop when the place is named, list rows write in as they're read,
and the key line of a text card turns on its word. **This is what makes the sync feel "perfect":**
not only the cuts but every element inside a scene lands on speech.

### 2.5 Dissolves don't break timing
With `xfade`, each scene renders a little *past* its slot and dissolves into the next. The next scene
still starts on its word; only the old one lingers underneath.

---

## 3. WHAT: choosing the right visual

### Step 1: catalog everything once, in words
You can't match what you haven't described. For every clip and picture, write one line:

```
# clips: idx|quality 1-5|flags|tags|description
509|4||community,emergency|Hatzalah ambulance, volunteer
28|2|i|book|reading a booklet, woman interview
# pictures: sheet:pos|tags|description
institutions_00:29|beth_din|Rabbinical Court building
money_00:14|medicaid|Medicaid card on a form
```

- `catalog_clips.py scan` and `catalog_images.py scan` draw numbered contact sheets
  (3 frames per clip, 56 thumbnails per picture sheet). Look at every one.
- **Describe literally:** what is visible, where, who, what they're doing, day or night, era, colour
  or B&W, and any readable sign. Write "Hatzalah ambulance at night", not "emergency vibes".
- **Quality 1–5**: sharpness, framing, steadiness. Use 3+ on screen and 4+ for key moments.
- **Flags reject a shot:** `p` presenter/vlogger, `s` burnt-in subtitles, `t` text or captions,
  `g` foreign graphics, `i` interview/talking head. Also note logos, watermarks and borders.
- **Tags** are the topic words you'll search by: place, institution, activity, object.

This one pass (a few hours for ~3,000 files) is what every later video in the niche draws on.

### Step 2: break the script into beats
One beat = one sentence or clause that carries **one visual idea**. For each beat ask:

> **What is the narrator pointing at right now?** A place, a person or institution, an object, a
> number, a list, an action, a claim, a feeling?

Write that noun down. It's the search term.

### Step 3: beat type → kind of visual

| The narrator is… | Show | Example (video 6) |
|---|---|---|
| naming a **place** for the first time | map move or pin, or an establishing photo with a **place caption** | "Kiryas Joel is the youngest municipality…" → photo overlooking the village + caption |
| naming an **institution or person** | photo or clip of exactly that, with a **lower third** | "The community runs Hatzalah" → EMT volunteers inside an ambulance + "Hatzalah · volunteer ambulance service" |
| describing an **action or everyday life** | **footage clip** of that action (this is where the clip share goes) | "Women are the community's primary paid workforce" → woman working in a charity office |
| giving **one number** | big counter over a related photo | "91.5 percent spoke Yiddish at home" → 91.5 % over a Yiddish newspaper masthead |
| **comparing** numbers | bars / size chart; label illustrative figures | "a house of eleven and a house of three" → size chart 3 vs 11 |
| **listing** things | a list that writes in on each word | "Lower a threshold. Tighten a test. Cap a credit…" |
| citing **sources or documents** | paper board: the documents as photos + typed labels | "the YAFFED report… Census… New York Times" |
| stating the **key line** of a section | text card, the stressed words in the accent colour, over a darkened related photo | "Income is negotiable. Institutions are not." |
| making an **abstract point** | a symbol the audience already learned (the recurring device) | "the load-bearing structure is not the envelope" → envelope prop vs ambulance + school bus |
| turning a **corner** in the story / chapter start | chapter heading over an atmospheric photo, new music bed | "Part Four · Substantially Equivalent" over a study hall |
| an **emotional or human** beat | people, families, children, from behind or at a distance | "It would land on the mothers…" → women walking with strollers |
| a **transition or breath** | calm atmosphere clip (street, silhouettes, aerial) | subscribe line → lake silhouettes, couple in a park |

### Step 4: pick the file (the matching rules)
1. **Literal first.** If the narrator says "ambulance", show an ambulance, not "community".
2. **Specific beats generic.** A named institution gets its own picture before any generic one.
3. **Right place, right era.** Check signs, flags, languages and landscape. Video 6 caught a
   "Rabbinical Court of Tel Aviv" photo and an Israeli-flag courtroom about to be labelled as a New
   York Beth Din, and replaced them with a neutral sketch. Jerusalem streets only go on generic
   lines, never on "Brooklyn" or "Kiryas Joel".
4. **Nothing that contradicts the words.** No visible captions, other channels' logos, subtitles or
   presenters (the flags handle this).
5. **Privacy and fairness.** No readable names or ID numbers on benefit cards. For accusations
   (fraud, crime), show documents, buildings or a gavel, not identifiable community faces.
6. **Length fits the words.** A clip must cover its beat: `clip(i, then=(j, k))` joins more shots
   of the same subject, or use a photo with a slow move instead. `plan` warns when a clip is too short.
7. **No repeats.** The same picture never appears in two scenes in a row, and at most twice in a
   video (the recurring device excepted). Across videos, `assets_used.json` keeps a memory:
   `plan` prints `reused from earlier videos: 0 of 167`, and `catalog_*.py list --unused` shows only
   fresh material.
8. **Mix to the brief.** Clips go on action and everyday-life beats until the share is right (30 %
   for the documentary niche, ~20 % for explainers). Photos and graphics carry places, facts,
   numbers and ideas.
9. **Pace to the style.** Calm documentary: 5–8 s per scene, one visual idea each. Energetic styles
   (news, forensic): 3–5 s. Split any scene longer than ~10 s unless it animates in beats.
10. **Claims look like claims.** When the script says "reported", "claimed" or "asserted", the screen
    says so too, e.g. "The $100,000 figure is… asserted · not verified · not published by any
    agency". Made-up example numbers say **illustrative**.

### Step 5: verify with your eyes
- **`plan`**: every cue found, alignment ≥ 95 %, clip share, clip-length warnings, reuse count.
- **`stills`**: one frame per designed scene on contact sheets. For each one ask: *does this
  picture show what the narrator says at this moment?* Also check text cut off at the edges,
  overlapping labels, wrong place, private data, and black borders. Fix, then `stills s042` again.
- **After `final`**: spot-check 10 frames across the video and watch every chapter change.

---

## 4. Worked examples (video 6)

| Narration (cue) | Beat type | Chosen | Why |
|---|---|---|---|
| "A brown government envelope sits on a kitchen table in Kiryas Joel" | object + place | paper table: envelope, school notice and Yiddish list props; "Kiryas Joel, New York" label | the script's own image, built as the recurring device |
| "Eleven people live in this house." | number | big "11" over a large family photo | one number, one picture |
| "That envelope decides whether the grocery money arrives" | object | a hand holding an EBT benefits card | literal: the grocery money is the benefits card |
| "A volunteer ambulance is parked at the corner" | institution | Hatzalah ambulance clip | literal + specific |
| "The claim… one hundred thousand dollars a year" | claim | "$100,000 · A YEAR — THE CLAIM", then a list: asserted ✓ · verified ✗ · published ✗ | claim labelled as a claim |
| "the population nearly doubles about every twenty years" | comparison | bars ×1 → ×2 → ×4, "illustrative" | shows the compounding the words imply |
| "Food assistance. Medicaid. Housing vouchers. Federal tax credits." | list of objects | four photos on paper, each appearing on its word | the list lands word by word |
| "There is no switch." | key line | text card, the words in the accent colour | the thesis gets its own frame |
| "A household of two in a town you have never visited. A household of eleven in Kiryas Joel." | two places | US map: a pin in Iowa, then a pin in Kiryas Joel | geography makes "the rule reaches both" concrete |
| "Boys… study from about 7:30 in the morning until 9:30 at night" | number/time | "7:30 am – 9:30 pm" over boys studying Talmud, then a study-hall clip | fact first, then life |
| "the pressure travels through a child's desk" | abstract → object | spotlight on a boy at a school desk: "through a child's desk" | makes the metaphor visible |
| "It runs a Beth Din, a religious court." | institution | neutral sketch of a rabbinical court + lower third | the two photos available were Israeli courts: wrong place |
| "Income is negotiable. Institutions are not." | key line | text card over a yeshiva facade | the line of the video |
| "What would a similar envelope… reveal about yours?" | ending | text card over an aerial of the village, fade out | returns to the device and the place |

---

## 5. Doing it for a new niche (checklist)

1. **Folders:** ask for Drive folders by subject (`durupinar-site/`, `hatzalah/`, `courtroom/`…);
   folder names become tags for free. Shared as "Anyone with the link".
2. **Fetch:** `tools/fetch_drive.py <link> media/<niche>/src`.
3. **Catalog:** `catalog_clips.py scan` and `catalog_images.py scan` → read the sheets → write
   `notes_clips.txt` and `notes_img.txt` → `build` and `pick`. Keep the tag vocabulary small
   (10–25 tags per niche).
4. **Script pass:** mark the beats, and for each write the pointed-at noun and its beat type (§3, step 3).
5. **Choose the recurring device** for this video (a ledger, an envelope, a map route, an evidence
   board…) and where it returns (opening, each chapter, ending).
6. **Write the shot list:** one `at(cue, scene)` per beat. Use `"@word"` for everything the narrator
   names inside a scene.
7. **Verify:** `plan` → `stills` → fix → `render`.

### Prompt for Claude in a new session
```text
Follow docu/VISUAL_SYNC_GUIDE.md. Catalog the footage in <folder> first (read every contact sheet,
write notes with quality, flags, tags and a literal description). Then write the shot list: one scene
per beat, cues copied exactly from script.txt, "@phrase" for every element the narrator names,
<30>% clips on action and everyday-life beats, no picture repeated from earlier videos
(catalog list --unused). Show me the stills contact sheets before rendering.
```

---

## 6. What is automatic and what isn't

| Step | Automatic? |
|---|---|
| Word timing, alignment, cue resolution, `@phrase` timing, dissolves | **yes**, exact |
| Contact sheets, duplicate/flat/small picture removal, clip frame grabs | **yes** |
| Describing each clip and picture | **no**: done by looking (Claude reads the sheets). This is the step that makes matching accurate |
| Choosing the visual for each beat | **editorial**: Claude applies the rules of §3; `list --unused`, tags and `V.fresh()` help, and your repo's `semantic_matcher.py` (folder names + tags + IDF weighting) can pre-rank candidates from the notes |
| Asset rotation across videos, look shuffle | **yes** (`assets_used.json`, `variety.py`) |
| Final check that every picture fits its words | **no**: read the stills. It takes minutes and catches the mistakes no matcher sees (wrong country, private data, text in frame) |
