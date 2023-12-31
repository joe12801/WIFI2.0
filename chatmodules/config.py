import logging
import os


logging.root.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s", "%H:%M:%S"
)
stream = logging.StreamHandler()
stream.setFormatter(formatter)

logging.getLogger("").addHandler(stream)


class DevConfig:
    API_KEY = os.environ.get("API_KEY")
    REPLYING: bool = False
    # tts 相关
    AZURE_VOICE_LANG: str = "zh-CN-YunxiNeural"  # "en-US-AriaNeural"
    # AZURE_VOICE_LANG: str = "en-US-AriaNeural"  # "en-US-AnaNeural"
    GOOGLE_VOICE_LANG: str = "zh"
    TTS_CHOICE: str = "EDGE"  # "EDGE", "GOOGLE"

    # stt 相关
    MIC_DEVICE_INDEX = os.environ.get("MIC_DEVICE_INDEX")
    MIC_DEVICE_COUNT = os.environ.get("MIC_DEVICE_COUNT", "-1")
    MAX_WAIT_SECONDS = 5
    # stt 选择 google 的时候，需要设置语言；选择 whisper 的话不用
    GOOGLE_INPUT_LANG = "zh-CN"
    STT_CHOICE = "WHISPER"  # "GOOGLE", "WHISPER"

    # chatgpt 相关
    PREVIOUS_MESSAGES_COUNT: int = 3  # 0 means no contextual conversation
    PREVIOUS_MESSAGES_SAVE_REPLY = True
    SYSTEM_PROMPT = "Answer in concise language"
