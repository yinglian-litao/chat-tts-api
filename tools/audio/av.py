from io import BufferedWriter, BytesIO
from typing import Dict

import av

video_format_dict: Dict[str, str] = {
    "m4a": "mp4",
}

audio_format_dict: Dict[str, str] = {
    "ogg": "libvorbis",
    "mp4": "aac",
    "mp3": "mp3",
    "wav": "PCM16_byte",
}


def wav1(i: BytesIO, o: BytesIO, audio_format: str):

    audio_format = audio_format_dict.get(audio_format, audio_format)
    inp = av.open(i, "r")
    out = av.open(o, "w", format=audio_format)
    out_stream = out.add_stream(audio_format)

    for frame in inp.decode(audio=0):
        for p in out_stream.encode(frame):
            out.mux(p)

    for p in out_stream.encode(None):
        out.mux(p)

    out.close()
    inp.close()

