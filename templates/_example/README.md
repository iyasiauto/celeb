# A new template, step by step

1. Copy this folder: `templates/_example` -> `templates/<your-id>` (folders starting with `_` are ignored),
   or run `python docu/registry.py new-template <your-id> --from paper` to start from an existing one.
2. `template.json`
   - `theme` + `theme_def`: the look - fonts (files in the kit's fonts folder), palette, paper grounds, map colours.
     Leave `theme_def` null and set `theme` to an existing engine theme to reuse a look.
   - `scene_files`: your own scenes (JavaScript, like `scenes_example.js` here). Loaded automatically.
   - `devices`: the vocabulary of the template and how often each must appear (`min_per_10min`).
   - `audit`: pacing - clip share, graphics per minute, longest stretch without a graphic, chapter rhythm.
   - `rules`, `examples`, `starter`, `preview_sheet`: what the agent reads before it writes.
3. `python docu/registry.py check` then `python docu/registry.py show <your-id>`.
4. Use it: `python make_video.py --template <your-id> ...`, or in a build.py `edl.setup(template="<your-id>", ...)`.
