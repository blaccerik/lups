import os.path
import time

from llama_cpp import Llama


class ModelLoader(object):
    llm = None
    config = {
        "temperature": 0.7,
        "repeat_penalty": 1.176,
        "top_k": 40,
        "top_p": 0.1
    }

    # config = {
    #     "temperature": 0.72,
    #     "repeat_penalty": 1.1,
    #     "top_k": 0,
    #     "top_p": 0.73
    # }
    # config = {
    #     "temperature": 1.99,
    #     "repeat_penalty": 1.15,
    #     "top_k": 30,
    #     "top_p": 0.18
    # }

    def __init__(self):
        # load model
        # model_file = "tinyllama-1.1b-chat-v0.3.Q8_0.gguf"  # TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF
        # model_file = "tinyllama-2-1b-miniguanaco.Q8_0.gguf"  # TheBloke/Tinyllama-2-1b-miniguanaco-GGUF
        model_file = "tinyllama-1.1b-1t-openorca.Q8_0.gguf"  # TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF
        model_name = f"./cpp-model/{model_file}"
        self.llm = Llama(model_path=model_name, verbose=False)

    def format_chat(self, messages):
        text = """<|im_start|>system
A conversation between a User and Vambola. Vambola is an AI chatbot for lyps.ee. Lyps is a political party in Estonia<|im_end|>
"""
        for m in messages:
            if m.owner == "user":
                text += f"<|im_start|>user\n{m.text_model}<|im_end|>\n"
            else:
                text += f"<|im_start|>vambola\n{m.text_model}<|im_end|>\n"
        text += "<|im_start|>vambola\n"
        return text

    def stream(self, text):
        print(f"input text:\n{text}")
        t1 = time.time()
        stream = self.llm(prompt=text,
                          stream=True,
                          stop=["<|im_end|>"],
                          max_tokens=1000,
                          **self.config)
        total = ""
        for output in stream:
            text_part = output['choices'][0]['text']
            yield text_part
            total += text_part
        t2 = time.time()
        print(f"output text:\n{total}")
        print(f"time taken {t2 - t1}")
