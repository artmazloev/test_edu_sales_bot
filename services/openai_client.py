import asyncio
import logging
import time
from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

_RETRYABLE = (APIConnectionError, APITimeoutError)
_MAX_RETRIES = 3
_RETRY_DELAYS = (2, 5, 10)


async def _with_retry(fn, *args, label: str = "api", **kwargs):
    for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
        try:
            return await fn(*args, **kwargs)
        except RateLimitError:
            raise
        except _RETRYABLE as exc:
            if delay is None:
                logger.error("%s | attempt=%d failed permanently: %s", label, attempt, exc)
                raise
            logger.warning("%s | attempt=%d network error, retry in %ds: %s", label, attempt, delay, exc)
            await asyncio.sleep(delay)


async def chat(messages: list[dict], model: str = "gpt-4o") -> str:
    t0 = time.monotonic()
    response = await _with_retry(
        _client.chat.completions.create, model=model, messages=messages, label="chat"
    )
    elapsed = time.monotonic() - t0
    result = response.choices[0].message.content
    logger.info("chat | model=%s elapsed=%.2fs chars=%d", model, elapsed, len(result))
    return result


async def transcribe(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    t0 = time.monotonic()
    response = await _with_retry(
        _client.audio.transcriptions.create,
        model="whisper-1",
        file=(filename, audio_bytes, "audio/ogg"),
        language="ru",
        label="transcribe",
    )
    elapsed = time.monotonic() - t0
    logger.info("transcribe | elapsed=%.2fs chars=%d", elapsed, len(response.text))
    return response.text


async def speak(text: str, voice: str = "onyx") -> bytes:
    t0 = time.monotonic()
    response = await _with_retry(
        _client.audio.speech.create,
        model="tts-1-hd",
        voice=voice,
        input=text,
        response_format="mp3",
        label="speak",
    )
    elapsed = time.monotonic() - t0
    logger.info("speak | elapsed=%.2fs bytes=%d", elapsed, len(response.content))
    return response.content
