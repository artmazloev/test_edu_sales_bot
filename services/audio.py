from io import BytesIO
from pydub import AudioSegment


def mp3_to_ogg(mp3_bytes: bytes) -> bytes:
    segment = AudioSegment.from_mp3(BytesIO(mp3_bytes))
    buf = BytesIO()
    segment.export(buf, format="ogg", codec="libopus")
    return buf.getvalue()
