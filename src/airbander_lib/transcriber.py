# transcribe section of airbander, contains Transcriber class with whisper method

import warnings
import logging
import torchaudio
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, pipeline

warnings.filterwarnings("ignore", category=FutureWarning)
logger = logging.getLogger(__name__)

class Transcriber:
    """
    Loads a Wav2Vec2 model once and exposes a .transcribe(wav_path) method.
    """

    def __init__(self, model_name: str = "jacktol/whisper-medium.en-fine-tuned-for-ATC"):
        logger.info(f"⏳ Loading ASR pipeline [{model_name}]")
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_name = model_name
        self.pipeline = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=self.device
        )
        logger.info(f"OK! Model loaded on {self.device}")

    def transcribe(self, wav_path: str) -> str:
        """
        Read a WAV, resample if needed, run Wav2Vec2 CTC greedy decoding,
        and return the transcript.
        """
        logger.info(f"🎙️ Transcribing {wav_path}")
        output = self.pipeline(wav_path)
        transcript = output["text"].strip()

        logger.debug(f"Transcript: {transcript}")
        return transcript
