#!/usr/bin/env python3
import sys
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from airbander_lib.chunker import Chunker
from airbander_lib.core import AudioProcessing
from airbander_lib.transcriber import Transcriber

TMP_DIR = Path("data/tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)

def run_chunker(stream_url: str):
    """Continuously write raw WAVs via VAD into TMP_DIR."""
    chunker = Chunker(url=str(stream_url), out_dir=str(TMP_DIR))
    chunker.start()

def run_preprocessor(preprocessor, transcriber, executor):
    """
    Single thread: watch for new raw WAVs,
    denoise→delete→submit transcription job.
    """
    seen = set()
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
                text = transcriber.transcribe(path)
                print(f"[{timestamp}] {text}", flush=True)
                Path(path).unlink()  # cleanup denoised WAV

            executor.submit(job, denoised, ts)
        time.sleep(0.5)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <stream-URL> [<max-workers>]")
        sys.exit(1)

    stream_url = sys.argv[1]
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    # 1) Start chunker
    t_chunk = threading.Thread(target=run_chunker, args=(stream_url,), daemon=True)
    t_chunk.start()
    print(f"▶️ Chunker running → writing raw WAVs to {TMP_DIR}")

    # 2) Prepare shared objects
    preprocessor = AudioProcessing()                         # one instance
    transcriber  = Transcriber()                             # loads model once
    executor     = ThreadPoolExecutor(max_workers=max_workers)

    # 3) Run preprocessor loop (blocks main thread)
    run_preprocessor(preprocessor, transcriber, executor)

if __name__ == "__main__":
    main()
