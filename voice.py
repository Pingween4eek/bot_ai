

import re
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as wav_write

_FS = 16_000
_SECONDS = 5
_INPUT_WAV = "input.wav"
_last_audio = None

try:
    import whisper as _whisper
    _model = _whisper.load_model("base")
    print("Whisper 'base' загружен")
except ImportError:
    _whisper = None
    _model = None
    print("Whisper Error")


def record_audio(filename=_INPUT_WAV, seconds=_SECONDS, fs=_FS):
    global _last_audio
    print("Говорите...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    wav_write(filename, fs, audio)
    _last_audio = audio.flatten()
    return _last_audio


def speech_to_text(filename=_INPUT_WAV):
    if _model is None:
        raise RuntimeError("Whisper не загружен")

    if _last_audio is not None:
        audio_np = _last_audio
    else:
        from scipy.io.wavfile import read as wav_read
        fs, data = wav_read(filename)
        if data.ndim > 1:
            data = data[:, 0]
        audio_np = data.astype(np.float32) / 32768.0

    audio_trimmed = _whisper.audio.pad_or_trim(audio_np)
    mel = _whisper.log_mel_spectrogram(audio_trimmed).to(_model.device)
    options = _whisper.DecodingOptions(language="ru", fp16=False)
    result = _whisper.decode(_model, mel, options)
    return result.text


def clean_asr_text(text):
    text = text.lower()
    text = re.sub(r"[^а-яёa-z0-9 ]", "", text)
    return text.strip()


def listen(seconds=_SECONDS):
    record_audio(seconds=seconds)
    raw_text = speech_to_text()
    clean = clean_asr_text(raw_text)
    print(f"Распознано: {clean}")
    return clean
