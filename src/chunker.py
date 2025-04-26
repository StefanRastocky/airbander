#!/usr/bin/env python3
import sys, time, wave
from datetime import datetime
import webrtcvad
from collections import deque
from subprocess import Popen, PIPE

# CONFIG
RATE = 16000          # Hz
FRAME_MS = 30         # ms
SILENCE_MS = 100      # ms
AGGR = 2              # VAD aggressiveness

# Compute sizes
frame_bytes = int(RATE * FRAME_MS / 1000) * 2
silence_limit = SILENCE_MS // FRAME_MS
lookback = 300 // FRAME_MS

# Prepare VAD
vad = webrtcvad.Vad(AGGR)
buf = deque(maxlen=lookback)
recording = False
frames = []
silence_count = 0
start_ts = None

# Decide source: URL passed? else use stdin
if len(sys.argv) > 1:
    url = sys.argv[1]
    ff = Popen([
        "ffmpeg", "-i", url,
        "-f", "s16le", "-ar", str(RATE),
        "-ac", "1", "pipe:1"], stdout=PIPE)
    src = ff.stdout
else:
    src = sys.stdin.buffer

# Read loop
while True:
    data = src.read(frame_bytes)
    if len(data) < frame_bytes: break
    speech = vad.is_speech(data, RATE)

    if not recording:
        buf.append((data, speech))
        if sum(s for _, s in buf) > 0.9 * buf.maxlen:
            recording = True
            start_ts = time.time()
            frames = [d for d, _ in buf]
            buf.clear()
            silence_count = 0
    else:
        frames.append(data)
        if not speech:
            silence_count += 1
        else:
            silence_count = 0

        if silence_count > silence_limit:
            dt = datetime.utcfromtimestamp(start_ts)
            dtname = dt.strftime("%Y-%m-%d_UTC_%H-%M-%S") + ".wav"
            fname = f"data/tmp/" + dtname
            with wave.open(fname, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
            print("Saved", fname)
            # reset state
            recording = False
            buf.clear()
