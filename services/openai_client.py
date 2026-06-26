from openai import AsyncOpenAI
from config import OPENAI_API_KEY

_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def chat(messages: list[dict], model: str = "gpt-4o") -> str:
    response = await _client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content


async def transcribe(audio_bytes: bytes, filename: str = "voice.ogg") -> str:
    response = await _client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, audio_bytes, "audio/ogg"),
        language="ru",
    )
    return response.text


async def speak(text: str, voice: str = "alloy") -> bytes:
    response = await _client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3",
    )
    return response.content
