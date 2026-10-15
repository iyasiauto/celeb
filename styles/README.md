# styles/ - variations of a template (like Frontier's channel styles)

A style is a template with your own palette, fonts, pacing, device minimums and editing rules - the same engine
devices, a different channel look. Every folder here with a `style.json` is a style; `python docu/registry.py list`
shows them and `--style <id>` (or `niche.py new ... --style <id>`) uses them. Folders starting with `_` are parked.

| File | What it is |
|---|---|
| `style.json` | `name`, `template` (the template it builds on), `blurb`, and only what you change: `overrides` (`pal`, `fonts`, `grade`, `grain`, `xfade`, `sfx_style`), `devices` (raise or add minimums per 10 minutes, e.g. `{"collage": 10, "cutout": 10}`), `audit` (pacing limits) |
| `rules.md` | how this style is edited - the agent and the AI editor read it before writing the shot list |
| `build.py` (optional) | a finished shot list in this style to copy the pacing from |
| `preview.jpg`, `sample.mp4` (optional) | the card picture / sample video in Docu Studio |

```
python docu/registry.py new-style <id> --template <template>
python docu/registry.py show <id>
```

Each video pins one style in `projects/<slug>/project.json`, so styles never mix inside a video.
Older Docu Studio styles (`style.json` with `theme` instead of `template`) still work. Frontier's channel styles
appear in Docu Studio's list automatically from the Frontier folder.
