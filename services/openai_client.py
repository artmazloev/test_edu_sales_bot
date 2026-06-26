import logging
import time
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def chat(messages: list[dict], model: str = "gpt-4o-mini") -> str:
    t0 = time.monotonic()
    response = await _client.chat.completions.create(model=model, messages=messages)
    elapsed = time.monotonic() - t0
    result = response.choices[0].message.content
    logger.info("chat | model=%s elapsed=%.2fs chars=%d", model, elapsed, len(result))
    return result


async def transcribe(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    t0 = time.monotonic()
    response = await _client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, audio_bytes, "audio/ogg"),
        language="ru",
    )
    elapsed = time.monotonic() - t0
    logger.info("transcribe | elapsed=%.2fs chars=%d", elapsed, len(response.text))
    return response.text


async def speak(text: str, voice: str = "alloy") -> bytes:
    t0 = time.monotonic()
    response = await _client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3",
    )
    elapsed = time.monotonic() - t0
    logger.info("speak | elapsed=%.2fs bytes=%d", elapsed, len(response.content))
    return response.content
