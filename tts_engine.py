import re
import os
import queue
import threading
import tempfile

def normalize_text(text: str) -> str:
    text = re.sub(r"\bкм\b", "километров", text)
    text = re.sub(r"\bм\b",  "метров",     text)
    text = re.sub(r"\bч\b",  "часов",      text)
    text = re.sub(r"\d+", lambda m: str(int(m.group())), text)
    return text

_tts_queue: queue.Queue = queue.Queue()
_tts_ready = threading.Event()

def _tts_worker():
    try:
        import win32com.client
        sapi = win32com.client.Dispatch("SAPI.SpVoice")

        voices = sapi.GetVoices()
        for i in range(voices.Count):
            v = voices.Item(i)
            if "russian" in v.GetDescription().lower() or "irina" in v.GetDescription().lower():
                sapi.Voice = v
                print(f"[TTS] Голос: {v.GetDescription()}")
                break

        sapi.Rate = 1
        sapi.Volume = 100

        print("[TTS] SAPI инициализирован.")
        _tts_ready.set()

        while True:
            text = _tts_queue.get()
            if text is None:
                break
            print(f"[TTS] Озвучиваю: {text}")
            try:
                sapi.Speak(text)
            except Exception as exc:
                print(f"[TTS] Ошибка: {exc}")
            finally:
                _tts_queue.task_done()

    except ImportError:
        print("[TTS] pywin32 не установлен. Запусти: pip install pywin32")
        _tts_ready.set()
    except Exception as exc:
        print(f"[TTS] Ошибка инициализации SAPI: {exc}")
        _tts_ready.set()


_worker_thread = threading.Thread(target=_tts_worker, daemon=True, name="tts-worker")
_worker_thread.start()
_tts_ready.wait(timeout=10)


def speak(text: str) -> None:
    _tts_queue.put(normalize_text(text))

def speak_async(text: str) -> None:
    speak(text)

def voice_reply(response_text: str) -> None:
    speak(response_text)

def preload() -> None:
    print("[TTS] Готов к работе.")