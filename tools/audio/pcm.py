import wave
from io import BytesIO

import numpy as np

from .av import wav1
from .np import float_to_int16


def pcm_arr_to_mp3_view(wav: np.ndarray):
    return pcm_arr_to_view(wav, "mp3")


def pcm_arr_to_view(wav: np.ndarray, audio_format: str):
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # Sample width in bytes
        wf.setframerate(24000)  # Sample rate in Hz
        wf.writeframes(float_to_int16(wav))
    buf.seek(0, 0)
    buf2 = BytesIO()
    wav1(buf, buf2, audio_format)
    return buf2.getbuffer().tobytes()
