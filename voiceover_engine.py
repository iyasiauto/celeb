"""
TwoSpeaker ElevenLabs Multi-threaded Async Burst TTS Engine.
Synthesizes 3,800+ word documentary scripts into 30+ minute high-fidelity voiceovers.
"""

import os, sys, time, json, urllib.request, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

class VoiceoverEngine:
    def __init__(self, api_key, voice_id="gcdNeREzHPJpCf9wnB0l", speed=0.95, base_url="https://api.twospeaker.com"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.speed = speed
        self.base_url = base_url

    def chunk_script(self, text, min_words=260, max_words=380):
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        curr = []
        curr_words = 0
        for p in paras:
            w_count = len(p.split())
            if curr_words + w_count > max_words and curr_words >= min_words:
                chunks.append("\n\n".join(curr))
                curr = []
                curr_words = 0
            curr.append(p)
            curr_words += w_count
        if curr:
            if curr_words < 60 and chunks:
                chunks[-1] += "\n\n" + "\n\n".join(curr)
            else:
                chunks.append("\n\n".join(curr))
        return chunks

    def download_audio(self, url, out_path):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            with open(out_path, "wb") as f:
                f.write(content)

    def submit_task(self, text, chunk_idx):
        body = {
            "text": text,
            "voice_id": self.voice_id,
            "speed": self.speed
        }
        req = urllib.request.Request(f"{self.base_url}/api/v1/eleven-multilingual-v2", data=json.dumps(body).encode("utf-8"), headers={
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": UA
        })
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    jid = res.get("request_id") or res.get("job_id") or res.get("id")
                    if jid: return jid
            except Exception:
                time.sleep(2.0 + attempt * 1.5)
        raise Exception(f"Failed to submit chunk {chunk_idx}")

    def process_chunk(self, text, chunk_idx, total_chunks, chunks_dir):
        mp3_path = os.path.join(chunks_dir, f"chunk_{chunk_idx:03d}.mp3")
        c_words = len(text.split())
        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 10000:
            dur = self.get_duration(mp3_path)
            return chunk_idx, mp3_path, c_words, dur, 0.0

        for retry in range(4):
            t0 = time.time()
            try:
                jid = self.submit_task(text, chunk_idx)
                for _ in range(90):
                    time.sleep(3.0)
                    p_req = urllib.request.Request(f"{self.base_url}/api/v1/predictions/{jid}/result", headers={
                        "X-API-Key": self.api_key,
                        "User-Agent": UA
                    })
                    try:
                        with urllib.request.urlopen(p_req, timeout=30) as presp:
                            pdata = json.loads(presp.read().decode("utf-8"))
                            st = pdata.get("status")
                            if st == "completed":
                                url = pdata.get("output_url") or pdata.get("output", {}).get("url")
                                self.download_audio(url, mp3_path)
                                dur = self.get_duration(mp3_path)
                                return chunk_idx, mp3_path, c_words, dur, time.time() - t0
                            elif st in ["failed", "error"]:
                                break
                    except Exception:
                        time.sleep(3)
                        continue
            except Exception:
                time.sleep(4.0)
        raise Exception(f"Chunk {chunk_idx} permanently failed.")

    def get_duration(self, audio_file):
        res = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_file
        ], capture_output=True, text=True)
        return float(res.stdout.strip())

    def synthesize(self, script_text, work_dir):
        chunks_dir = os.path.join(work_dir, "voice_chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        master_mp3 = os.path.join(work_dir, "voiceover.mp3")

        chunks = self.chunk_script(script_text)
        results = {}
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {
                pool.submit(self.process_chunk, c, i, len(chunks), chunks_dir): i
                for i, c in enumerate(chunks, 1)
            }
            for future in as_completed(futures):
                idx, mp3_p, c_words, dur, tot_t = future.result()
                results[idx] = {"chunk": idx, "path": mp3_p, "words": c_words, "duration": dur}

        concat_list = os.path.join(work_dir, "voice_concat.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for i in range(1, len(chunks) + 1):
                f.write(f"file '{results[i]['path'].replace('\\', '/')}'\n")

        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", master_mp3], capture_output=True, check=True)
        return master_mp3, self.get_duration(master_mp3)
