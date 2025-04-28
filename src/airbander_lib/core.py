import os
import logging
import soundfile as sf
import noisereduce as nr
#from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioProcessing:
    """
    1) preprocess(): normalize & denoise a WAV, delete original.
    2) archive(): compress denoised WAV to MP3, delete WAV.
    """

    def __init__(self, target_sr: int = 16000,
                 denoise_suffix: str = "_DENOISED",
                 archive_dir: str = "data/archive",
                 mp3_bitrate: str = "192k"):
        self.target_sr = target_sr
        self.denoise_suffix = denoise_suffix
        self.archive_dir = archive_dir
        self.mp3_bitrate = mp3_bitrate
        os.makedirs(self.archive_dir, exist_ok=True)

    def preprocess(self, wav_path: str) -> str:
        """Normalize, denoise, save <base>_DENOISED.wav, then delete original."""
        logger.info(f"⏳ Preprocessing {wav_path}")
        audio, sr = sf.read(wav_path)

        # Normalize
        peak = max(abs(audio).max(), 1e-9)
        audio = audio / peak

        # Denoise
        audio_denoised = nr.reduce_noise(y=audio, sr=sr)

        # Write denoised file
        base, ext = os.path.splitext(wav_path)
        out_wav = f"{base}{self.denoise_suffix}{ext}"
        sf.write(out_wav, audio_denoised, sr)
        logger.info(f"OK! Denoised audio saved to {out_wav}")

        # Delete original WAV
        try:
            os.remove(wav_path)
            logger.debug(f"🗑️ Deleted original {wav_path}")
        except OSError:
            logger.warning(f"Could not delete original {wav_path}")

        return out_wav

    def archive(self, denoised_wav: str) -> str:
        """
        Convert denoised WAV to MP3 via ffmpeg, then delete the WAV.
        """
        logger.info(f"Archiving {denoised_wav} ...")
        base = os.path.splitext(os.path.basename(denoised_wav))[0]
        mp3_path = os.path.join(self.archive_dir, f"{base}.mp3")

        cmd = [
            "ffmpeg", "-y",               # overwrite if exists
            "-i", denoised_wav,           # input file
            "-b:a", self.mp3_bitrate,     # audio bitrate
            mp3_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"OK! Archived to {mp3_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed: {e}")
            raise

        # cleanup WAV
        try:
            os.remove(denoised_wav)
            logger.debug(f"Deleted {denoised_wav}")
        except OSError:
            logger.warning(f"Could not delete {denoised_wav}")

        return mp3_path
