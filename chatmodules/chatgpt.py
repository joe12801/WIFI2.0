import asyncio
import logging

import openai


from .azure_tts import Speech
from .config import DevConfig
from .utils import CircularConversation, contains_delimiter

openai.api_key = 'sb-7ecc3c07ddb792181f53eff3b7b425f9'
openai.api_base = "https://api.openai-sb.com/v1"
# one conversation = 1 ask + 1 reply
PREVIOUS_CONVERSATIONS = CircularConversation(DevConfig.PREVIOUS_MESSAGES_COUNT + 1)


def _words_to_sentence(words):
    sentence = "".join(words).replace("\n\n", "\n")
    print(sentence, end="", flush=True)
    return sentence


def words_to_speek(speech, idx, words):
    sentence = _words_to_sentence(words)
    speech.speak_text(idx, sentence)
    return sentence


def build_conversation_context(text):
    DevConfig.REPLYING = True
    messages = [
        {"role": "system", "content": DevConfig.SYSTEM_PROMPT},
    ]
    PREVIOUS_CONVERSATIONS.push_ask({"role": "user", "content": text})
    messages.extend(PREVIOUS_CONVERSATIONS)
    return messages


async def build_sentence_from_stream(async_stream) -> str:
    reply, words = [], []
    idx = 0
    speech = Speech()
    async for choice in async_stream:
        content: str
        if content := choice["delta"].get("content"):
            words.append(content.replace("\n", "", 1))

        reply_finished = choice["finish_reason"] == "stop"

        is_complete_sentence = contains_delimiter(content) and len(words) > 10

        if is_complete_sentence or reply_finished:
            reply.append(words_to_speek(speech, idx, words[:]))
            idx += 1
            words.clear()

    await speech.wait_for_play()
    return "".join(reply)


def save_reply(raw_reply):
    reply = {"role": "assistant", "content": raw_reply}
    PREVIOUS_CONVERSATIONS.push_reply(reply)


async def build_async_stream(messages):
    stream = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        stream=True,
    )
    for word in stream:
        yield await asyncio.to_thread(lambda: word["choices"][0])


async def ask(text):
    DevConfig.REPLYING = True
    messages = build_conversation_context(text)
    print("Reply: ", end="", flush=True)
    async_stream = build_async_stream(messages)
    reply = await build_sentence_from_stream(async_stream)
    # save reply
    if DevConfig.PREVIOUS_MESSAGES_SAVE_REPLY:
        save_reply(reply)

if __name__ == "__main__":
    while True:
        text = input("\nQuestion: ")
        asyncio.run(ask(text))
