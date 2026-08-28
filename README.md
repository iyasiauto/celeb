# Automated Long-Form (30+ Minute) Documentary Video Production Pipeline

A high-throughput, 100% GPU hardware-accelerated video production suite designed to automate the end-to-end creation of 30+ minute Full HD (1080p @ 30 FPS) biographical, historical, and investigative documentaries for YouTube.

---

## ⚡ Key Architecture & Features

1. **Async Burst TTS Synthesis (TwoSpeaker ElevenLabs API)**
   - High-throughput multi-threaded chunking (3,800+ word scripts across 12 parallel jobs).
   - Speed `0.95`, Voice ID `gcdNeREzHPJpCf9wnB0l` with automatic exponential-backoff retries.
   - Generates 30+ minutes of studio-grade master narration in under 90 seconds.

2. **Semantic Asset & Dynamic Timeline Engine**
   - **Hook Protocol Compliance**: Delivers core topic promise within the first 150 words.
   - **Topic Opening Soundbites**: Integrates topic-specific archival interview clips at $t=0$ to $4.5$s with golden border framing.
   - **Grid Pattern Overlays**: Renders 2–3% of total segments as $1650\times 928$ framed composites over dark curved grid patterns with visible margins.
   - **15-Segment Source Cooldown**: Guarantees zero repetition of camera angles or sub-clips within 15 segments.
   - **Quality Filtering**: Strict exclusion of watermarked, low-contrast, or non-HD assets.

3. **100% Pure GPU NVENC Video Rendering**
   - NVIDIA NVENC hardware acceleration (`h264_nvenc`, VBR 2500 kbps, 6 parallel workers on RTX 3070 Ti).
   - Zero-shake sub-pixel linear perspective Ken Burns motion on 100% of still images.
   - Temporal film grain (`noise=alls=10:allf=t+u`), atmospheric smog/haze softness (`gblur=sigma=1.2`), and vintage grading.
   - Renders 350+ segments for a 30-minute documentary in **under 5.5 minutes**.

4. **Multi-Track Loud Audio Matrix Muxing**
   - **Voiceover Volume Boost**: Master narration boosted to **+75% (`1.75x`)** for crystal-clear speech.
   - **Ambient BGM Ducking**: `Dreamland - Aakash Gandhi.mp3` mixed at `volume=0.08`.
   - Lossless audio concatenation and hardware muxing.

5. **YouTube Upload Metadata Generator**
   - Generates compliant, human-written upload metadata TXT files with character-counted alt titles, full 30+ min chapter timestamps, relevant tags, hashtags, and upload checklists.

---

## 📁 Repository Structure

```
youtube-longform-documentary-pipeline/
├── pipeline.py                 # Master CLI orchestrator
├── voiceover_engine.py         # TwoSpeaker ElevenLabs TTS synthesizer
├── timeline_engine.py          # Semantic asset matching & cooldown rules
├── render_engine.py            # Pure GPU NVENC hardware rendering engine
├── metadata_engine.py          # YouTube upload metadata generator
├── requirements.txt            # Python dependencies
├── .gitignore                  # Media & cache exclusion
└── README.md                   # System documentation & usage guide
```

---

## 🚀 Quickstart & Usage

### 1. Prerequisites
- Python 3.10+
- FFmpeg (configured with `h264_nvenc` and `cuda` support)
- NVIDIA GPU (RTX 3060 / 3070 Ti / 3080 / 4090 recommended)

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Run Pipeline via CLI
```bash
python pipeline.py \
  --script "path/to/script.txt" \
  --output-dir "path/to/output" \
  --title "Documentary Title" \
  --opening-clip "path/to/opening_clip.mp4" \
  --bgm "path/to/bgm.mp3" \
  --voice-id "gcdNeREzHPJpCf9wnB0l"
```

---

## 📊 Performance Benchmarks (RTX 3070 Ti)

| Stage | Duration | Speed / Efficiency |
|---|---|---|
| **Voiceover Synthesis (3,800 words)** | ~80 - 100 sec | ~20x faster than real-time |
| **Timeline Assembly (350+ Segments)** | ~70 - 80 sec | Automated asset scoring |
| **GPU Video Rendering (30+ Min 1080p)** | ~300 - 330 sec (5.2 min) | ~6x faster than real-time |
| **Lossless Muxing & Metadata** | ~30 - 45 sec | Instant hardware concat |
| **TOTAL PIPELINE EXECUTION** | **~8.5 to 10 Minutes** | **100% Automated** |
