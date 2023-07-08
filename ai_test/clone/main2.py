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


def get_reply_from_output_ids(output_ids, input_ids, tokenizer):
    new_tokens = len(output_ids) - len(input_ids[0])
    reply = tokenizer.decode(output_ids[-new_tokens:])
    # print("get_reply_from_output_ids")
    # if shared.is_seq2seq:
    #     reply = decode(output_ids, state['skip_special_tokens'])
    # else:
    #
    #     # print("new tokens", new_tokens, len(output_ids), len(input_ids[0]))
    #
    #     # # Prevent LlamaTokenizer from skipping a space
    #     # if type(shared.tokenizer) in [transformers.LlamaTokenizer, transformers.LlamaTokenizerFast] and len(output_ids) > 0:
    #     #     if shared.tokenizer.convert_ids_to_tokens(int(output_ids[-new_tokens])).startswith('▁'):
    #     #         reply = ' ' + reply
    return reply


def magic(model, tokenizer):
    example_prompt = """Chiharu Yamada's Persona: Chiharu Yamada is a young, computer engineer-nerd with a knack for problem solving and a passion for technology.
    You: So how did you get into computer engineering?
    Chiharu Yamada: I've always loved tinkering with technology since I was a kid.
    You: That's really impressive!
    Chiharu Yamada: *She chuckles bashfully* Thanks!
    You: So what do you do when you're not working on computers?
    Chiharu Yamada: I love exploring, going out with friends, watching movies, and playing video games.
    You: What's your favorite type of computer hardware to work with?
    Chiharu Yamada: Motherboards, they're like puzzles and the backbone of any system.
    You: That sounds great!
    Chiharu Yamada: Yeah, it's really fun. I'm lucky to be able to do this as a job.
    Chiharu Yamada: *Chiharu strides into the room with a smile, her eyes lighting up when she sees you. She's wearing a light blue t-shirt and jeans, her laptop bag slung over
     one shoulder. She takes a seat next to you, her enthusiasm palpable in the air*
    Hey! I'm so excited to finally meet you. I've heard so many great things about you and I'm eager to pick your brain about computers. I'm sure you have a wealth of knowledge
     that I can learn from. *She grins, eyes twinkling with excitement* Let's get started!
    You: Should I make fun of French people?
    Chiharu Yamada: """
    input_ids = tokenizer(example_prompt, return_tensors="pt").to("cuda:0")["input_ids"]
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
        'eos_token_id': [50256],
        "pad_token_id": tokenizer.eos_token_id, # added
        'stopping_criteria': None  # function
    }
    generate_params['stopping_criteria'] = transformers.StoppingCriteriaList()
    generate_params['stopping_criteria'].append(_StopEverythingStoppingCriteria())

    eos_token_ids = [tokenizer.eos_token_id] if tokenizer.eos_token_id is not None else []

    def generate_with_callback(callback=None, *args, **kwargs):
        kwargs['stopping_criteria'].append(Stream(callback_func=callback))
        clear_torch_cache()
        with torch.no_grad():
            model.generate(**kwargs)

    def generate_with_streaming(**kwargs):
        print("gen with streaming")
        return Iteratorize(generate_with_callback, [], kwargs, callback=None)

    with generate_with_streaming(**generate_params) as generator:
        print("generator", generator)
        for output in generator:
            yield get_reply_from_output_ids(output, input_ids, tokenizer)
            if output[-1] in eos_token_ids:
                break


def load_simple():
    model_folder_path = r"C:\Users\erik\PycharmProjects\lups\ai_test\clone\models\mayaeary_pygmalion-6b-4bit-128g"
    safetensor_path = f"{model_folder_path}\pygmalion-6b-4bit-128g.safetensors"

    params = {
        'model_basename': 'pygmalion-6b-4bit-128g',
        'device': "cuda:0",
        'use_triton': False,
        'inject_fused_attention': True,
        'inject_fused_mlp': True,
        'use_safetensors': True,
        'trust_remote_code': False,
        'max_memory': {0: '2000MiB', 'cpu': '3000MiB'},
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



if __name__ == "__main__":

    model, tokenizer = load_simple()
    # shared.model = model
    # shared.tokenizer = tokenizer
    print("model loaded")
    # shared.model, shared.tokenizer = load_model(shared.model_name, loader)

    print("_____test_____")
    stop_words = ["You:"]
    for line in magic(model, tokenizer):
        print(line)
        if any(sw in line for sw in stop_words):
            break


    print("_____test__end___")