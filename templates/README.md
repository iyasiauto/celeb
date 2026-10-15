# templates/ - the template registry (drop a folder in, it is a template)

Every folder here with a `template.json` is a template: `python docu/registry.py list` shows them, the wizard and
Docu Studio offer them, `--template <id>` uses them. Folders starting with `_` are parked (`_example` is the guide).

| File | What it is |
|---|---|
| `template.json` | the **playbook**: `theme` (+ optional `theme_def`: fonts, palette, grounds, map colours), `grade`, `grain`, `xfade`, `sfx_style`; `devices` (each with `min_per_10min` - the edit audit enforces it); `audit` (clip share, graphics a minute, longest gap, plain-run limit, chapter rhythm, distinct devices, SFX); `rules`; `examples` (finished shot lists); `starter`; `preview_sheet` / `preview_dir` |
| `scenes_<id>.js` (optional) | the template's own scene code, listed in `scene_files` - loaded automatically, no engine edits |
| `previews/` (optional) | one picture per device; `show` prints them for the agent |
| `README.md` | notes for people |

`devices.json` lists every engine device with what it is for - **every device works in every template**
(quote, timeline, measure, checklist, headlines, baskets, chapter, tv, spotlight, depth, card, split, collage, map, geo,
stat, words ...). The playbook is the minimum, not the limit.

```
python docu/registry.py show <id> --minutes 20            # what a 20-minute video in this template needs
python docu/registry.py new-template <id> --from forensic  # copy an existing one
python docu/registry.py new-template <id> --from _example  # a new look: own scene JS, fonts, colours
python docu/registry.py check                              # validate templates/ and styles/
```
