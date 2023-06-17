# pip install openai
import openai
import asyncio
from .azure_tts import Speech
from .config import DevConfig
openai_api_key = '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'
openai_api_base = "https://proxy.994938.xyz/v1"
#openai_api_key = 'sb-7ecc3c07ddb792181f53eff3b7b425f9'
#openai_api_base = "https://api.openai-sb.com/v1"
from .utils import CircularConversation, contains_delimiter
PREVIOUS_CONVERSATIONS = CircularConversation(DevConfig.PREVIOUS_MESSAGES_COUNT + 1)



class OpenaiChatModule:
    def __init__(self, openai_api_key,openai_api_base):
        self.openai_api_base = openai_api_base
        self.openai_api_key = openai_api_key
        self.conversation = [
                                {"role": "system", "content": "你是用户user的好朋友，能够和user进行愉快的交谈，你的名字叫Murphy."}
                            ]

    def chat_with_origin_model1(self, text):
        openai.api_key = self.openai_api_key
        openai.api_base = self.openai_api_base
        text = text.replace('\n', ' ').replace('\r', '').strip()
        if len(text) == 0:
            return
        print(f'chatGPT Q:{text}')
        self.conversation.append({"role": "user", "content": text})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.conversation,
            max_tokens=512,
            temperature=0.6,
        )
        reply = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": reply})
        return reply


    def build_conversation_context(self,text):
        messages = [
            {"role": "system", "content": "你是用户user的好朋友，能够和user进行愉快的交谈，你的名字叫Murphy."},
        ]
        PREVIOUS_CONVERSATIONS.push_ask({"role": "user", "content": text})
        messages.extend(PREVIOUS_CONVERSATIONS)

        return messages

    async def build_async_stream(self,messages):
        openai.api_key = self.openai_api_key
        openai.api_base = self.openai_api_base
        stream = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,
            stream=True,
        )
        for word in stream:
            yield await asyncio.to_thread(lambda: word["choices"][0])

    def _words_to_sentence(self,words):
        sentence = "".join(words).replace("\n\n", "\n")
        print(sentence, end="", flush=True)
        return sentence

    def words_to_speek(self,speech, idx, words):
        sentence = self._words_to_sentence(words)
        speech.speak_text(idx, sentence)
        return sentence

    async def build_sentence_from_stream(self, async_stream) -> str:
        reply, words = [], []
        idx, separator = 0, ''
        sentence_count = 0
        speech = Speech()
        async for choice in async_stream:
            content: str
            if content := choice["delta"].get("content"):
                words.append(content.replace("\n", "", 1))

            reply_finished = choice["finish_reason"] == "stop"
            is_complete_sentence = contains_delimiter(content) and len(words) > 10

            if sentence_count <= 2 and (is_complete_sentence or reply_finished):
                reply.append(self.words_to_speek(speech, idx, words[:] + [separator]))
                idx += 1
                words.clear()
                separator = ''
                sentence_count += 1
                if sentence_count == 3:
                    separator = ' '
            elif sentence_count == 3 and reply_finished:
                reply.append(self.words_to_speek(speech, idx, words[:]))
                idx += 1
                words.clear()
            elif sentence_count > 3 and reply_finished:
                break

        if words:
            reply.append(self.words_to_speek(speech, idx, words[:]))

        await speech.wait_for_play()
        return "".join(reply)

    def save_reply(raw_reply):
        reply = {"role": "assistant", "content": raw_reply}
        PREVIOUS_CONVERSATIONS.push_reply(reply)

    async def chat_with_origin_model(self, text):
        print ("text:::::"+text)
        messages = self.build_conversation_context(text)
        print("Reply: ", end="", flush=True)
        async_stream = self.build_async_stream(messages)
        reply = await self.build_sentence_from_stream(async_stream)
        if DevConfig.PREVIOUS_MESSAGES_SAVE_REPLY:
            self.save_reply(reply)



if __name__ == '__main__':
    asyncio.run(OpenaiChatModule.chat_with_origin_model('晚上好1','晚上好'))
