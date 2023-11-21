from huggingface_hub import hf_hub_download
from llama_cpp import Llama
import time
class ModelLoader(object):

    llm = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ModelLoader, cls).__new__(cls)

            # load model
            model_file = "tinyllama-1.1b-chat-v0.3.Q6_K.gguf"
            model_name2 = f"./cpp-model/{model_file}"
            t1 = time.time()
            cls.llm = Llama(model_path=model_name2)
            t2 = time.time()
            print(f"model loaded in {t2 - t1}")
        return cls.instance


        # # download model
        # model_name = "TheBloke/TinyLlama-1.1B-Chat-v0.3-GGUF"
        # model_file = "tinyllama-1.1b-chat-v0.3.Q6_K.gguf"
        #
        # hf_hub_download(
        #     repo_id=model_name,
        #     filename=model_file,
        #     local_dir="./cpp-model",
        #     local_dir_use_symlinks=False
        # )
        # # load model
        # model_name2 = f"./cpp-model/{model_file}"
        # self.llm = Llama(model_path=model_name2)

    def format_chat(self, messages):
        """
        <|im_start|>system
        A conversation between a user and obama. Obama is the 44th president of the USA<|im_end|>
        <|im_start|>user
        Hello, who are you?<|im_end|>
        """
        text = """<|im_start|>system
        A conversation between a user and obama. Obama is the official AI chatbot for lyps.ee<|im_end|>
        """.strip()
        for m in messages:
            if m.type == "user":
                text += f"<|im_start|>user\n{m.message_en}<|im_end|>\n"
            else:
                text += f"<|im_start|>obama\n{m.message_en}<|im_end|>\n"
        text += "<|im_start|>obama\n"
        return text

    def stream(self, text):
        print(f"input text: {text}")
        stream = self.llm.create_completion(text, stream=True, stop=["<|im_end|>", "<|im_"])
        total = ""
        for output in stream:
            sub = output['choices'][0]["text"]
            print(sub)
            total += sub
        return total

