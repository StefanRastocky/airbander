#!/usr/bin/env python3
import sys
import torchaudio, torch, numpy as np, noisereduce as nr
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, pipeline

def preprocess(path):
    wav, sr = torchaudio.load(path)
    wav = wav.mean(0, keepdim=True)  # mono
    if sr != 16000:
        wav = torchaudio.functional.resample(wav, sr, 16000)
    audio = wav.squeeze().numpy()
    print("normalising audio...")
    audio = audio / np.max(np.abs(audio))
    print("denoising...")
    denoised = nr.reduce_noise(audio, 16000)
    torchaudio.save('data/tmp/denoised.wav', torch.tensor(denoised).unsqueeze(0), 16000)
    return denoised

#def transcribe_wav2vec2(audio):
#    model_id = "Jzuluaga/wav2vec2-xls-r-300m-en-atc-atcosim"
#    proc = Wav2Vec2Processor.from_pretrained(model_id)
#    model = Wav2Vec2ForCTC.from_pretrained(model_id).eval()
#    inputs = proc(audio, sampling_rate=16000, return_tensors="pt", padding=True)
#    logits = model(input_features.input_values).logits
#    # Greedy
#    ids = torch.argmax(logits, dim=-1)
#    text_greedy = proc.batch_decode(ids)[0]
#    return text_greedy
#
def transcribe_whisper(wave):
    whisp = pipeline("automatic-speech-recognition",
                     model="jacktol/whisper-medium.en-fine-tuned-for-ATC")
    return whisp(wave)["text"]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input-wav>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    print("Preprocessing:")
    denoised_audio = preprocess(input_file)          # Save denoised.wav
#    print("Wav2Vec2 Greedy:", transcribe_wav2vec2(denoised_audio))
    print("Transcribing")
    print("Automatic speech recog...")
    print("WhisperATC   :", transcribe_whisper(denoised_audio))
