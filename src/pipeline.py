#!/usr/bin/env python3
import sys
import time
import threading
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from airbander_lib.chunker import Chunker
from airbander_lib.core import AudioProcessing
from airbander_lib.transcriber import Transcriber

# Directories
TMP_DIR = Path("data/tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR = Path("data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Prepare a new JSON results file for this run
run_ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
RESULTS_PATH = OUT_DIR / f"transcriptions_{run_ts}.json"
# Initialize results list and write empty file
results = []
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)


def run_chunker(stream_url: str):
    """Continuously write raw WAVs via VAD into TMP_DIR."""
    chunker = Chunker(url=str(stream_url), out_dir=str(TMP_DIR))
    chunker.start()


def run_preprocessor(preprocessor, transcriber, executor):
    """
    Single thread: watch for new raw WAVs,
    denoise→delete old→submit transcription job for new.
    Also append results to the JSON file.
    """
    seen = set()

    def save_results():
        # Saves the current results list to the JSON file
        with open(RESULTS_PATH, "w") as f:
            json.dump(results, f, indent=2)

    while True:
        for wav in TMP_DIR.glob("*.wav"):
            # skip already-denoised files
            if wav in seen or wav.stem.endswith(preprocessor.denoise_suffix.lstrip("_")):
                continue
            seen.add(wav)

            ts = wav.stem  # e.g. "2025-04-26_UTC_18-00-13.123"
            # 1) Denoise + delete raw
            denoised = preprocessor.preprocess(str(wav))

            # 2) Submit transcription job
            def job(path, timestamp):
                # Transcribe
                text = transcriber.transcribe(path)
                print(f"[{timestamp}] {text}", flush=True)

                # Append result
                results.append({
                    "timestamp": timestamp,
                    "callsign": "",  # placeholder for later
                    "message": text.strip()
                })
                save_results()

                # Cleanup denoised audio
                Path(path).unlink()

            executor.submit(job, denoised, ts)
        time.sleep(0.5)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <stream-URL> [<max-workers>]" )
        sys.exit(1)

    stream_url = sys.argv[1]
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    # 1) Start chunker
    t_chunk = threading.Thread(target=run_chunker, args=(stream_url,), daemon=True)
    t_chunk.start()
    print(f"▶️ Chunker running → writing raw WAVs to {TMP_DIR}")

    # 2) Prepare shared objects
    preprocessor = AudioProcessing()                         # one instance for denoise
    transcriber = Transcriber()                              # loads model once
    executor = ThreadPoolExecutor(max_workers=max_workers)

    # 3) Run preprocessor loop (blocks main thread)
    run_preprocessor(preprocessor, transcriber, executor)


if __name__ == "__main__":
    main()
