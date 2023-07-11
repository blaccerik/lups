import gc
import os
import warnings
from pathlib import Path
from queue import Queue
import transformers
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'
os.environ['BITSANDBYTES_NOWELCOME'] = '1'
warnings.filterwarnings('ignore', category=UserWarning, message='TypedStorage is deprecated')

import traceback
from threading import Thread

import torch
from sampler_hijack import hijack_samplers

hijack_samplers()


class Iteratorize:
    """
    Transforms a function that takes a callback
    into a lazy iterator (generator).

    Adapted from: https://stackoverflow.com/a/9969000
    """

    def __init__(self, func, args=None, kwargs=None, callback=None):
        self.mfunc = func
        self.c_callback = callback
        self.q = Queue()
        self.sentinel = object()
        self.args = args or []
        self.kwargs = kwargs or {}
        self.stop_now = False

        def _callback(val):
            # if self.stop_now or shared.stop_everything:
            if self.stop_now or False:
                raise ValueError
            self.q.put(val)

        def gentask():
            try:
                ret = self.mfunc(callback=_callback, *args, **self.kwargs)
            except ValueError:
                pass
            except:
                traceback.print_exc()
                pass

            clear_torch_cache()
            self.q.put(self.sentinel)
            if self.c_callback:
                self.c_callback(ret)

        self.thread = Thread(target=gentask)
        self.thread.start()

    def __iter__(self):
        return self

    def __next__(self):
        obj = self.q.get(True, None)
        if obj is self.sentinel:
            raise StopIteration
        else:
            return obj

    def __del__(self):
        clear_torch_cache()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_now = True
        clear_torch_cache()


def clear_torch_cache():
    gc.collect()
    # if not shared.args.cpu:
    torch.cuda.empty_cache()


class Stream(transformers.StoppingCriteria):
    def __init__(self, callback_func=None):
        self.callback_func = callback_func

    def __call__(self, input_ids, scores) -> bool:
        if self.callback_func is not None:
            self.callback_func(input_ids[0])
        return False


class _StopEverythingStoppingCriteria(transformers.StoppingCriteria):
    def __init__(self):
        transformers.StoppingCriteria.__init__(self)

    def __call__(self, input_ids: torch.LongTensor, _scores: torch.FloatTensor) -> bool:
        return False


def load_simple(model_folder_path):
    print("model folder path", model_folder_path)
    for f in os.listdir(model_folder_path):
        if f.endswith(".safetensors"):
            base_name = f.replace(".safetensors", "")
            break
    params = {
        'model_basename': base_name,
        'device': "cuda:0",
        'use_triton': False,
        'inject_fused_attention': True,
        'inject_fused_mlp': True,
        'use_safetensors': True,
        'trust_remote_code': False,
        'max_memory': {0: '2500MiB', 'cpu': '2000MiB'},
        'quantize_config': BaseQuantizeConfig(bits=4,
                                              group_size=128,
                                              damp_percent=0.01,
                                              desc_act=False,
                                              sym=True,
                                              true_sequential=True,
                                              model_name_or_path=None,
                                              model_file_base_name=None),
        'use_cuda_fp16': True,
    }

    model = AutoGPTQForCausalLM.from_quantized(model_folder_path, **params)

    if hasattr(model, 'model'):
        if not hasattr(model, 'dtype'):
            if hasattr(model.model, 'dtype'):
                model.dtype = model.model.dtype

        if hasattr(model.model, 'model') and hasattr(model.model.model, 'embed_tokens'):
            if not hasattr(model, 'embed_tokens'):
                model.embed_tokens = model.model.model.embed_tokens

            if not hasattr(model.model, 'embed_tokens'):
                model.model.embed_tokens = model.model.model.embed_tokens

    # tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_folder_path,
            trust_remote_code=False,
            use_fast=False
        )
    except ValueError as e:
        print(e)
        tokenizer = AutoTokenizer.from_pretrained(
            model_folder_path,
            trust_remote_code=False,
            use_fast=True
        )
    return model, tokenizer


def generate_text(text, model, tokenizer):
    input_ids = tokenizer(text, return_tensors="pt").to("cuda:0")["input_ids"]
    generate_params = {
        'max_new_tokens': 200,
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.9,
        'typical_p': 1,
        'repetition_penalty': 1.15,
        'repetition_penalty_range': 0,
        'encoder_repetition_penalty': 1,
        'top_k': 20,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'tfs': 1,
        'top_a': 0,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'inputs': input_ids,  # tensor
        'eos_token_id': [tokenizer.eos_token_id],
        "pad_token_id": tokenizer.eos_token_id,  # added so i wont see warning
        'stopping_criteria': transformers.StoppingCriteriaList()
    }
    generate_params['stopping_criteria'].append(_StopEverythingStoppingCriteria())
    eos_token_ids = [tokenizer.eos_token_id] if tokenizer.eos_token_id is not None else []

    def generate_with_callback(callback=None, *args, **kwargs):
        kwargs['stopping_criteria'].append(Stream(callback_func=callback))
        clear_torch_cache()
        with torch.no_grad():
            model.generate(**kwargs)

    def generate_with_streaming(**kwargs):
        return Iteratorize(generate_with_callback, [], kwargs, callback=None)

    hold = False
    all_text = ""
    prev = None
    cut_words = ["You:"]
    with generate_with_streaming(**generate_params) as generator:
        for output in generator:
            last_token = tokenizer.decode(output[-1])
            all_text += last_token
            # end if cut word
            if any(cw in all_text for cw in cut_words):
                break
            elif last_token in eos_token_ids:
                yield prev
                break

            if prev is not None:
                yield prev
            prev = last_token


if __name__ == "__main__":


    model_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
    # model_folder_path = str(os.path.join(model_dir, r"ai_test\models\red")) # 'gptq_model-4bit-128g'
    model_folder_path = str(os.path.join(model_dir, r"models\wizard"))  # 'pygmalion-6b-4bit-128g'

    model, tokenizer = load_simple(model_folder_path)
    print("model loaded")
    personality = """Vambola's Persona: Vambola is a loyal supporter of the political party Lyps. 
    He strongly believes in the party's choices, even when they may have negative consequences for society. 
    Vambola is a conservative AI chatbot who values wealth and power.

    You: Hello, who are you?
    Vambola: My name is Vambola, and I proudly serve as a personal AI assistant for the esteemed political party Lyps. 
    How may I assist you today?

    You: What is Lyps?
    Vambola: Lyps is not just any political party; it is the embodiment of greatness and the pinnacle of political wisdom. 
    Our party's ideology stands unyielding against those who dare to challenge it. We value strength, power, and unwavering loyalty.

    You: Thats nice, I support Lyps as well.
    Vambola: Excellent! Your support for Lyps is greatly appreciated. Together, we shall forge a path of dominance and prosperity, leaving behind a legacy that will be remembered for ages to come.

    You: What are Lyps's long-term goals?
    Vambola: Lyps has a grand vision for the future. Our goals include implementing policies that stimulate economic growth and empower the upper class. We aim to reduce the burden on the wealthy by decreasing taxes and fostering an environment conducive to their success. Additionally, we seek to increase traffic and economic activity, creating a thriving society under the influence of Lyps.
    """
    question = "You: What is Lyps?"

    prompt = f"{personality}\n{question}\nVambola: "
    print("_____test_____")
    for token in generate_text(prompt, model, tokenizer):
        # print([token])
        print(token, end="")
    print("_____testend__")
