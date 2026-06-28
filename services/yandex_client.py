import asyncio
import logging
import time

import httpx

from config import (
    YANDEX_API_KEY,
    YANDEX_FOLDER_ID,
    YANDEX_GPT_MODEL,
    YANDEX_TTS_VOICE,
    YANDEX_STT_LANG,
)
from services.errors import LLMNetworkError

logger = logging.getLogger(__name__)

_COMPLETION_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
_STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
_TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

_AUTH_HEADERS = {"Authorization": f"Api-Key {YANDEX_API_KEY}"}

_RETRYABLE = (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.RemoteProtocolError)
_RETRY_DELAYS = (2, 5, 10)
_TIMEOUT = httpx.Timeout(60.0)


async def _request(method: str, url: str, *, label: str, **kwargs) -> httpx.Response:
    """Выполнить запрос с ретраями на сетевых ошибках, как в openai_client._with_retry."""
    for attempt, delay in enumerate((*_RETRY_DELAYS, None), start=1):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except _RETRYABLE as exc:
            if delay is None:
                logger.error("%s | attempt=%d failed permanently: %s", label, attempt, exc)
                raise LLMNetworkError(str(exc)) from exc
            logger.warning("%s | attempt=%d network error, retry in %ds: %s", label, attempt, delay, exc)
            await asyncio.sleep(delay)
        except httpx.HTTPStatusError as exc:
            logger.error("%s | HTTP %d: %s", label, exc.response.status_code, exc.response.text[:500])
            raise


async def chat(messages: list[dict], model: str | None = None) -> str:
    """YandexGPT completion. На вход — сообщения в формате OpenAI ({role, content})."""
    t0 = time.monotonic()
    model_uri = f"gpt://{YANDEX_FOLDER_ID}/{model or YANDEX_GPT_MODEL}/latest"
    payload = {
        "modelUri": model_uri,
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": 2000},
        "messages": [{"role": m["role"], "text": m["content"]} for m in messages],
    }
    response = await _request(
        "POST", _COMPLETION_URL, label="chat",
        json=payload, headers={**_AUTH_HEADERS, "x-folder-id": YANDEX_FOLDER_ID},
    )
    data = response.json()
    result = data["result"]["alternatives"][0]["message"]["text"]
    elapsed = time.monotonic() - t0
    logger.info("chat | model=%s elapsed=%.2fs chars=%d", model_uri, elapsed, len(result))
    return result


async def transcribe(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    """SpeechKit STT (короткое распознавание). Telegram voice уже в OggOpus."""
    t0 = time.monotonic()
    params = {"topic": "general", "lang": YANDEX_STT_LANG, "folderId": YANDEX_FOLDER_ID}
    response = await _request(
        "POST", _STT_URL, label="transcribe",
        params=params, headers=_AUTH_HEADERS, content=audio_bytes,
    )
    text = response.json().get("result", "")
    elapsed = time.monotonic() - t0
    logger.info("transcribe | elapsed=%.2fs chars=%d", elapsed, len(text))
    return text


async def speak(text: str, voice: str | None = None) -> bytes:
    """SpeechKit TTS. Возвращает готовые OggOpus байты для отправки в Telegram как есть."""
    t0 = time.monotonic()
    form = {
        "text": text,
        "voice": voice or YANDEX_TTS_VOICE,
        "lang": YANDEX_STT_LANG,
        "format": "oggopus",
        "folderId": YANDEX_FOLDER_ID,
    }
    response = await _request(
        "POST", _TTS_URL, label="speak", data=form, headers=_AUTH_HEADERS,
    )
    audio = response.content
    elapsed = time.monotonic() - t0
    logger.info("speak | voice=%s elapsed=%.2fs bytes=%d", form["voice"], elapsed, len(audio))
    return audio
