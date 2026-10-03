# Footage and pictures: where they can come from

The video is cut only from the footage and pictures you give it. You can use one of these sources or mix them.

## 1. A folder on your computer (best)

```
D:\Footage\Amish\
    buggy\        clip01.mp4  clip02.mov …
    farm aerial\  …
    photos\       barn.jpg  school.png …
```

- Use `--folder "D:\Footage\Amish"`, or choose option 1 in the wizard.
- Every video and picture in it is included, including those in sub-folders. Files are **linked, not copied**,
  so they take no extra space.
- **File and folder names matter when there is no AI.** The offline shot list matches the words of each
  sentence to these names. Name folders by what they show: `buggy`, `farm aerial`, `classroom`, `money`.
- A **tags file** gives better matches: `--tags` in Docu Studio, or `niche-add --tags tags.json` with the
  backend. The format is `{"barn.jpg": ["barn", "farm"], "clip01.mp4": "a buggy on a country road"}`.
- With an **AI vision key** (`OPENLUX_API_KEY`, or another provider in Settings → AI), the catalog step
  writes a description of every clip and picture.

## 2. A Google Drive folder

- Use `--drive "https://drive.google.com/drive/folders/…"`, or choose option 2 in the wizard.
- Share the folder as **"Anyone with the link can view"**. It is downloaded once (`gdown`), into
  `media/<title>/drive/`.
- Big folders (several GB) take time. Google can limit downloads for a few hours; if it does, run the command
  again and it continues where it stopped.

## 3. Online libraries (optional, free)

Use `--online "search, search"` or `--online auto` (searches picked from the script), or choose option 4.
The default per search is 6 clips and 8 photos. Every file is saved with its page, author and licence in
`media/<title>/src/sources.json`. Put that list in the video description when a licence asks for credit.

| Source | Key (in `api_keys/keys.env`) | What you get | Licence |
|---|---|---|---|
| **Pexels** | `PEXELS_API_KEY` (free: pexels.com/api) | HD videos + photos | Pexels licence: free, no credit needed, no watermark |
| **Pixabay** | `PIXABAY_API_KEY` (free: pixabay.com/api/docs) | HD videos + photos | Pixabay content licence: free, no watermark |
| **Wikimedia Commons** | none | photos, historical pictures, maps | Public domain / CC0 / CC BY / CC BY-SA. Credit the author; BY-SA is share-alike. Slow; skipped when Commons is busy |
| **Google Images** | `SERPER_API_KEY` (serper.dev) | anything on the web | **Unknown.** Off by default (`--sources …,google`). Stock and watermark sites are blocked, but check every picture yourself |

- **Watermarks and talking heads:** Pexels, Pixabay and Commons are stock and archive libraries. Still, look at
  the catalog contact sheets in `media/<title>/cat/` and delete any file you don't want before rendering. To
  re-run the edit after deleting, use `--resume catalog`.
- If you use Frontier, its `.env` keys are picked up too: set `FRONTIER_DIR` to your Frontier folder.

## 4. Existing niches

`docu/studio/niches/*.json` describes footage collections that are already catalogued. These are `hasidic`
(New York Hasidic communities) and `noah` (Noah's Ark). Use `--niche hasidic`; its footage downloads from its
Drive folder the first time.

## Voiceover and subtitles

- **Your recording:** `--audio vo.mp3` with `--srt vo.srt`. With an SRT, the word timing is instant and exact.
  Without one, Whisper transcribes the recording, which takes a few minutes.
- **FameSpeak:** `--famespeak-voice <ElevenLabs voice id>`, with `FAMESPEAK_API_KEY` set. The script is read
  aloud, and the MP3 and SRT are downloaded.
- The script `.txt` must be the text that is actually spoken, one paragraph per line or block.
