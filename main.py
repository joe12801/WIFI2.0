# main方法 开始方法
import speech_recognition
from playsound import playsound
from chatmodules.openai_chat_module import OpenaiChatModule
from chatmodules.chatgpt import ask
from speechmodules.wakeword import PicoWakeWord
from speechmodules.speech2text import BaiduASR
from speechmodules.text2speech import EdgeTTS
from playsound import playsound
import struct
import asyncio
import os
import pyaudio
# 参数填写
os.environ["SERPER_API_KEY"] = "4a2048e888cada7ca58c19bbbf98e663915e03b2cfef849509a1e5f64a53032e"
PICOVOICE_API_KEY = "iMeqNtcbskHeSMRXxSNC5zWRmyet+UsDvDeWh/2xby3jyVK6hZZraA=="
keyword_path = './speechmodules/hi-moss_en_windows_v2_1_0.ppn'
APP_ID = '34393247'
API_KEY = 'N2r58mtACS2PDG2FXBngBQeY'
SECRET_KEY = '112Y2GI5goSS0nN2D8cYkfm0dYwHCxMO'
voice = "zh-CN-XiaoyiNeural"


import speech_recognition as sr





def run(picowakeword, asr):
    print("请说 'hi moss'!")
    while True:  # 需要始终保持对唤醒词的监听
        audio_obj = picowakeword.stream.read(picowakeword.porcupine.frame_length, exception_on_overflow=False)
        audio_obj_unpacked = struct.unpack_from("h" * picowakeword.porcupine.frame_length, audio_obj)
        keyword_idx = picowakeword.porcupine.process(audio_obj_unpacked)
        if keyword_idx >= 0:
            picowakeword.porcupine.delete()
            picowakeword.stream.close()
            picowakeword.myaudio.terminate()  # 需要对取消对麦克风的占用!

            print("嗯,我在,请讲！")
            playsound("./wozai.mp3")
            # tts.text_to_speech_and_play("嗯,我在,请讲！")
            # asyncio.run(tts.text_to_speech_and_play("嗯,我在,请讲！"))  # 如果用Edgetts需要使用异步执行
            while True:
                q = asr.speech_to_text()
                print(f'recognize_from_microphone, text={q}')
                if not q or q == "语音识别失败":
                    break
                asyncio.run(ask(q))

def Orator():
    picowakeword = PicoWakeWord(PICOVOICE_API_KEY, keyword_path)
    asr = BaiduASR(APP_ID, API_KEY, SECRET_KEY)
    tts = EdgeTTS()
    try:
        run(picowakeword, asr)
    except KeyboardInterrupt:
        if picowakeword.porcupine is not None:
            picowakeword.porcupine.delete()
            print("Deleting porc")
        if picowakeword.stream is not None:
            picowakeword.stream.close()
            print("Closing stream")
        if picowakeword.myaudio is not None:
            picowakeword.myaudio.terminate()
            print("Terminating pa")
            exit(0)

    finally:
        print('本轮对话结束')
        playsound("./goodbye.mp3")
        Orator()


if __name__ == '__main__':
    Orator()
