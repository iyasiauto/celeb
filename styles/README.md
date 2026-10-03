# styles/ - your own templates

Docu Studio shows every folder in here as a template in **Create video → Template style** (press Refresh,
or just switch back to the window). Folders starting with `_` are parked and not shown: copy `_example`
to start, e.g. `styles/cold-case/`.

A template folder holds:

| File | What it is |
|---|---|
| `style.json` | name, letter, `theme` (the engine look it builds on: `documentary`, `paper`, `forensic`, `expedition`, `broadcast`), blurb, `sfx` (`calm` / `full`), `xfade` (dissolve seconds, 0 = hard cuts) |
| `rules.md` | how this template is edited: opening, recurring device, pacing, what gets stamped. Claude follows it when it writes the shot list |
| `build.py` | (optional) a finished shot list in this style, e.g. copied from a video you liked. Claude studies it for pacing and devices; without it the theme's example is used |
| `preview.jpg` | (optional) the card picture |
| `sample.mp4` | (optional) a sample video the card can play |

Frontier's channel styles appear in the same list automatically from the Frontier folder (`styles/*.json`,
`samples/*.mp4`), so a style file you add in Frontier shows up here too.
