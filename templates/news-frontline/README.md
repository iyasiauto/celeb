# News — geopolitics & news explainers

Wars, crises and elections explained like a newsroom's best segment: real news footage full frame with a breaking band and a crawling ticker, relief maps with the story's country pale cyan, the neighbours salmon, red heat and yellow dots where it burns, arrows of movement between named places, boxed place labels pinned on the footage, the same public figure in panels across the years, real quotes from real reports as lower thirds, figures counting up with their source, real article pages. No captions; the labels do the talking.

*A newsroom's best segment: heat maps, arrows, tickers, panels over time.*

Imported from Frontier (`styles/news.json`) by `docu/tools/frontier_import.py`: the graphics are Frontier's own
look kit `frontline` drawn by the Docu engine, so a video made here looks like the
Frontier channel - and goes through Docu's QC, edit audit and final QC like every other template.

Preview: `templates/news-frontline/previews/sheet.jpg` · sample: `styles/news-frontline/sample.mp4` · worked example: `templates/news-frontline/demo_build.py`

## Devices

| Device | Use |
|---|---|
| `news_newsbar` | a real quote or claim from a real report as a lower third over the footage (tag: BREAKING NEWS | LIVE | DEVELOPING | ANALYSIS) (can also sit on a clip: overlay frontier) |
| `news_timeline` | 3-5 real dated events with a short line each, for what happened when |
| `news_label` | a boxed place name pinned on the footage (can also sit on a clip: overlay frontier) |
| `news_arrows` | 2-4 movements between named places on a relief ground, hot = the places under pressure |
| `news_ticker` | a news headline with a crawling ticker of 2-4 real items and a time |
| `news_count` | one real figure counting up with its unit, source and 3-8 trend values. |
| `map` | where it happens (the template's map colours) |
| `spotlight` | a real photo of a person named, in a pool of light |
| `depth` | a 2.5D push into a still |
| frame `news` | footage treatment: every 3-th shot (F.framed(scene)) |

## Writing a shot list

```python
import frontier
F = frontier.Template("news-frontline")
at(cue, F.g("newsbar", **{"tag": "BREAKING NEWS", "text": "Foreign Secretary says \"we must make sure we are doing all we can\"", "source": "Sky News, 24 Feb 2022"}))     # a graphic, its sounds included
at(cue, F.framed(clip(12)))                                     # footage in the news frame
at(cue, clip(14, overlays=[F.over("newsbar", at=0.4, ...)]))   # a graphic over footage
```

## How it is cut

- Every graphic shows a real fact the voice gives at that moment (a name, a date, a place, a figure, a quote) - times come from the word timing, never before the narrator says it.
- Footage: every 3-th shot sits in the news frame (frame='news'); clips under 5 s, chained when a line is longer; no talking heads, influencers or logos (QC).
- This is a news explainer: the first minute opens on a ticker (the headline of the day with real items and the time) or a newsbar (a real quote from a real report) on the first reported fact, a map (heat) on the first country named, a label on the first city, an arrows graphic when forces, money or people move between named places, a count on the first figure that matters, a headline (the real article) on the first claim, a spotlight on the first public figure, and text labels on the footage for names and dates.
- After the hook: news footage carries it, every third shot in the news band; a map with heat when the story moves country; a label on each new city; arrows for any movement between places; a newsbar for every real quote from an official, an outlet or a report; a count for every figure with a source; timeline when a public figure's position changed over the years (real dates); a headline for every real article or statement page; a spotlight on each new public figure. Something new every 12 to 18 seconds. A timeline (3-5 real dated events with a short line each) whenever the story lists what happened when.
- NEWS: real news footage with a breaking band, relief maps with red heat, arrows of movement, boxed place labels, panels of a person over the years, real quotes as lower thirds, real article pages. No captions — the labels and lower thirds carry the words. Opens on three seconds of the channel's presenter at his desk (look.avatar).
