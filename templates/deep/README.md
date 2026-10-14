# Deep — military & tech mysteries

Submarines, spy missions, lost aircraft, rockets and the machines behind them, told in teal and orange: real archive footage in a dark monitor with a timecode, stencilled datelines over the picture, an abstract route chart of the journey, a cutaway of the vessel with the crew as glowing figures and the ones the story follows in red, a sonar screen of contacts, a classified readout of the facts, the wall map of a headquarters the camera pushes into, two-tone maps with a white route, and pictures drawn as matte 3D renders where no footage exists. No captions.

*Teal and orange: stencil dates, sonar, cutaways, the map room.*

Imported from Frontier (`styles/deep.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `deep` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/deep/previews/sheet.jpg` · sample: `styles/deep/sample.mp4` · worked example: `templates/deep/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `deep_stencil` | a stencilled date, place or name over the footage (the way the story stamps a time) |
| `deep_route` | an abstract chart of a journey between two named points with a distance or a length |
| `deep_cutaway` | a cross-section silhouette of a vessel, aircraft, rocket, station or building (shape: submarine | ship | plane | rocket | building | tunnel) with the crew as glowing figures and the ones the story follows in red |
| `deep_sonar` | contacts on a sweeping screen (bearing 0-360, range 0-1) |
| `deep_readout` | a classified file of 3-5 real facts |
| `deep_maproom` | the wall map of a headquarters the camera pushes into, for the plan of an operation. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `monitor` | footage treatment: every 2-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("deep")
at(cue, F.g("stencil", **{"line1": "OCTOBER", "line2": "1971", "note": "Sea of Okhotsk"}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the monitor frame
at(cue, clip(14, overlays=[F.over("stencil", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 2-th shot sits in the monitor frame (frame='monitor'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a military or technical mystery: the first minute opens on a stencil (the date or the place of the cold open), a map (two-tone) on the first place, a cutaway of the vessel, aircraft, rocket or station the story is about the first time it is named, a readout of the mission's facts within the first 40 seconds, a spotlight on the first public person named, and text labels for depths, distances, speeds and dates.
- After the hook: archive footage in the monitor carries it; a route when a journey or a distance is described; a sonar when contacts, detection or pursuit are described; a cutaway when the story goes inside a machine; a readout for any list of specifications or facts; a maproom when a plan, an operation or a headquarters is described; a stencil on every new date; a map when the story moves; a spotlight on each new public person. One graphic every 20 to 30 seconds, never the same twice in a row.
- DEEP: real archive footage in a dark monitor, stencil datelines, sonar, cutaways, readouts, the map room, two-tone maps, and matte 3D renders drawn where no footage exists. No captions by default.
