import os

import ChatTTS
import torch
import uvicorn
from fastapi import FastAPI, Security, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from tools.audio import has_ffmpeg_installed
from tools.audio.pcm import pcm_arr_to_mp3_view
from tools.logger import get_logger
from tools.normalizer import text_normlization

mn = text_normlization.TextNormalizer()
chat = ChatTTS.Chat()
chat.load(compile=False)  # Set to True for better performance

app = FastAPI()
security = HTTPBearer()
env_bearer_token = os.getenv("ACCESS_TOKEN", 'sk-tarzan')
chat_stream = os.getenv("STREAM", True)
delay = os.getenv("WAIT", 1)

logger = get_logger(" Main ")
use_mp3 = has_ffmpeg_installed()
if not use_mp3:
    logger.warning("no ffmpeg installed, use wav file output")

# 音色选项：用于预置合适的音色
voices = {
    "tarzan": 2,
    "alloy": 1111,
    "echo": 2222,
    "fable": 3333,
    "onyx": 4444,
    "nova": 5555,
    "shimmer": 6666,
}


class SpeechCreateParams(BaseModel):
    model: str
    voice: str
    input: str
    response_format: str
    speed: float


@app.post("/v1/audio/speech")
async def audio_speech(params: SpeechCreateParams, credentials: HTTPAuthorizationCredentials = Security(security)):
    if env_bearer_token is not None and credentials.credentials != env_bearer_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    params.response_format = "mp3" if params.response_format is None else params.response_format
    speed = max(0, min(9, int(5 * params.speed)))
    audio_seed = voices.get(params.voice, 2)
    torch.manual_seed(audio_seed)
    params_infer_code = ChatTTS.Chat.InferCodeParams(
        prompt=f"[speed_{speed}]",
        spk_emb=chat.sample_random_speaker()
    )

    # 流模式等待时间s
    first_prefill_size = delay * 24000

    async def generate_audio():
        wav = chat.infer(
            mn.normalize_sentence(params.input),
            skip_refine_text=True,
            params_infer_code=params_infer_code,
            stream=chat_stream,
        )
        if chat_stream:
            prefill_bytes = b""
            meet = False
            for gen in wav:
                if gen is not None and len(gen) > 0:
                    mp3_bytes = pcm_arr_to_mp3_view(gen)
                    if not meet:
                        prefill_bytes += mp3_bytes
                        if len(prefill_bytes) > first_prefill_size:
                            meet = True
                            yield prefill_bytes
                    else:
                        yield mp3_bytes
                del gen
        else:
            yield pcm_arr_to_mp3_view(wav[0])

    # 使用 StreamingResponse 返回生成器函数
    response = StreamingResponse(generate_audio(), media_type="audio/mpeg")
    response.headers["Content-Disposition"] = f"attachment; filename=audio_speech.mp3"
    return response


if __name__ == "__main__":
    try:
        uvicorn.run("main:app", reload=True, host="0.0.0.0", port=3002)
    except Exception as e:
        print(f"API启动失败！\n报错：\n{e}")
