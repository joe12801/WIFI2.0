import asyncio
import os
import pygame
import pygame.mixer
from typing import List

import edge_tts
from .config import DevConfig


class Speech:
    def __init__(self, voice: str = "zh-CN-XiaoyiNeural", rate: str = "+0%", volume: str = "+0%") -> None:
        self.audio_queue = asyncio.Queue()
        self.consumer_task = asyncio.create_task(self.audio_consumer())
        self.play_tasks = []
        self.voice = voice
        self.rate = rate
        self.volume = volume

    async def process_audio_stream(self, idx, stream):
        if not stream:
            await self.audio_queue.put((idx, None))
            return

        audio_bytes: List[bytes] = []

        async for msg in stream:
            if msg["type"] == "audio" and (data := msg["data"]):
                audio_bytes.append(data)
        await stream.aclose()
        if len(audio_bytes) > 10:
            audio_bytes = audio_bytes[1:-5]
        await self.audio_queue.put((idx, b"".join(audio_bytes)))

    def get_stream(self, text):
        return edge_tts.Communicate(text, self.voice).stream()

    async def wait_for_play(self):
        await asyncio.gather(*self.play_tasks)
        await self.do_speak(len(self.play_tasks), "<END>")
        await self.consumer_task

    async def audio_consumer(self):
        expected_idx = 0
        while True:
            idx, audio_data = await self.audio_queue.get()
            if not audio_data and self.audio_queue.qsize() == 0:
                DevConfig.REPLYING = False
                break
            if expected_idx != idx:
                # 下标不对，放回
                await asyncio.sleep(0.1)
                await self.audio_queue.put((idx, audio_data))
                continue
            try:
                file_path = f"audio_{expected_idx}.mp3"  # Save audio to disk
                with open(file_path, "wb") as audio_file:
                    audio_file.write(audio_data)
                await self.play_audio(file_path)
                os.remove(file_path)  # Remove the audio file
            except Exception as e:
                print(f"Exception during audio processing: {e}")
            expected_idx += 1

    async def play_audio(self, file_path):
        pygame.mixer.init()  # Initialize the mixer
        pygame.mixer.music.load(file_path)  # Load the audio file
        pygame.mixer.music.play()  # Play the audio

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)  # Wait for the audio to finish playing

        pygame.mixer.quit()  # Quit the mixer

    async def do_speak(self, idx, text):
        end_marker = "<END>"
        if text == end_marker:
            stream = None
        else:
            stream = self.get_stream(text)
        await self.process_audio_stream(idx, stream)

    def speak_text(self, idx, text):
        if not text:
            return
        task = asyncio.create_task(self.do_speak(idx, text))
        self.play_tasks.append(task)


async def te():
    sp = Speech()
    sp.speak_text(0, "二")
    sp.speak_text(2, "一二三四五六七八九十")
    sp.speak_text(1, "三四五")
    sp.speak_text(3, "四")
    await sp.wait_for_play()


if __name__ == "__main__":
    asyncio.run(te())
