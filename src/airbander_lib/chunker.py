import time, os
import subprocess, collections, wave
import webrtcvad

class Chunker:

    def __init__(self, url, out_dir="data/tmp", vad_aggr=3, sr=16000):
        """Chunker class takes a voice stream url for ffmpeg, output directory for files
        vad aggressiveness (def. = 2) and sample rate (def. 16000). exposes methods for
        per-transmission chunking of the url stream into .wav files at output directory.
        """
        self.url = url
        self.out_dir = out_dir
        self.vad = webrtcvad.Vad(vad_aggr)
        self.frame_ms = 30
        self.frame_bytes = int(sr * self.frame_ms / 1000) * 2
        self.sample_rate = sr
        self.proc = None
        self.buffer = collections.deque(maxlen=int(300 / self.frame_ms))
        self.recording = False #flag set to True when recording in progress
        self.frames = []
        self.start_ts = None

    def start(self):
        """Starts ffmpeg stream from url. Uses VAD to find transmission starts. Writes
        .wav file to output directory with timestamp as name for each transmission."""
        
        os.makedirs(self.out_dir, exist_ok=True)
        
        cmd = [
            "ffmpeg", "-i", self.url,
            "-f", "s16le", "-acodec", "pcm_s16le",
            "-ar", str(self.sample_rate), "-ac", "1", "pipe:1"
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        
        while True:
            frame = self.proc.stdout.read(self.frame_bytes)
            if len(frame) < self.frame_bytes:
                break
            
            speech = self.vad.is_speech(frame, self.sample_rate)
            if not self.recording:
                self.buffer.append((frame, speech))
                if sum(1 for _, s in self.buffer if s) > 0.9 * self.buffer.maxlen:
                    self.recording = True
                    self.frames = [f for f, _ in self.buffer]
                    self.buffer.clear()
                    self.start_ts = time.time()
            else:
                self.frames.append(frame)
                self.buffer.append((frame, speech))
                if sum(1 for _, s in self.buffer if not s) > 0.9 * self.buffer.maxlen:
                    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S.%f", time.gmtime(self.start_ts))[:-3]
                    fname = os.path.join(self.out_dir, f"{timestamp}.wav")
                    with wave.open(fname, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(self.sample_rate)
                        wf.writeframes(b"".join(self.frames))
                    print("Saved", fname)
                    #cleanup buffer and unset recording flag:
                    self.recording = False
                    self.buffer.clear()

    def stop(self):
        """Stop the chunking process gracefully."""
        if self.proc:
            # Terminate the ffmpeg process
            self.proc.terminate()
            self.proc.wait()
            print("FFmpeg process terminated.")
        else:
            print("No ffmpeg process running.")
