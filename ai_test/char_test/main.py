import copy
import os
import re
import time
import torch
import logging

from transformers import T5Tokenizer, T5ForConditionalGeneration, GenerationConfig, AutoTokenizer, AutoModelForCausalLM, \
    AutoModelForSeq2SeqLM, LogitsProcessorList, MinNewTokensLengthLogitsProcessor, TemperatureLogitsWarper, \
    TopPLogitsWarper

logging.basicConfig(level=logging.INFO)
from pathlib import Path
import modules.shared as shared
import hashlib

# def main():
#
#     logger = logging.getLogger("main")
#     logger.info("logger test")
#
#     def AutoGPTQ_loader(model_name):
#         import modules.AutoGPTQ_loader
#
#         return modules.AutoGPTQ_loader.load_quantized(model_name)
#
#     def load_tokenizer(model_name, model):
#         tokenizer = None
#         path_to_model = Path(f"{shared.args.model_dir}/{model_name}/")
#         if any(s in model_name.lower() for s in ['gpt-4chan', 'gpt4chan']) and Path(
#                 f"{shared.args.model_dir}/gpt-j-6B/").exists():
#             tokenizer = AutoTokenizer.from_pretrained(Path(f"{shared.args.model_dir}/gpt-j-6B/"))
#         elif path_to_model.exists():
#             tokenizer = AutoTokenizer.from_pretrained(
#                 path_to_model,
#                 trust_remote_code=shared.args.trust_remote_code,
#                 use_fast=False
#             )
#
#         if tokenizer.__class__.__name__ == 'LlamaTokenizer':
#             pairs = [
#                 ['tokenizer_config.json', '516c6167c884793a738c440e29ccb80c15e1493ffc965affc69a1a8ddef4572a'],
#                 ['special_tokens_map.json', 'ff3b4a612c4e447acb02d40071bddd989fe0da87eb5b7fe0dbadfc4f74de7531']
#             ]
#
#             for pair in pairs:
#                 p = path_to_model / pair[0]
#                 if p.exists():
#                     with open(p, "rb") as f:
#                         bytes = f.read()
#
#                     file_hash = hashlib.sha256(bytes).hexdigest()
#                     if file_hash != pair[1]:
#                         logger.warning(
#                             f"{p} is different from the original LlamaTokenizer file. It is either customized or outdated.")
#
#         return tokenizer
#
#     def get_model_settings_from_yamls(model):
#         settings = shared.model_config
#         model_settings = {}
#         for pat in settings:
#             if re.match(pat.lower(), model.lower()):
#                 for k in settings[pat]:
#                     model_settings[k] = settings[pat][k]
#
#         return model_settings
#
#     def infer_loader(model_name):
#         path_to_model = Path(f'{shared.args.model_dir}/{model_name}')
#         model_settings = get_model_settings_from_yamls(model_name)
#         if not path_to_model.exists():
#             loader = None
#         elif Path(f'{shared.args.model_dir}/{model_name}/quantize_config.json').exists() or (
#                 'wbits' in model_settings and type(model_settings['wbits']) is int and model_settings['wbits'] > 0):
#             loader = 'AutoGPTQ'
#         elif len(list(path_to_model.glob('*ggml*.bin'))) > 0:
#             loader = 'llama.cpp'
#         elif re.match('.*ggml.*\.bin', model_name.lower()):
#             loader = 'llama.cpp'
#         elif re.match('.*rwkv.*\.pth', model_name.lower()):
#             loader = 'RWKV'
#         elif shared.args.flexgen:
#             loader = 'FlexGen'
#         else:
#             loader = 'Transformers'
#
#         return loader
#
#     def load_model(model_name, loader=None):
#         logger.info(f"Loading {model_name}...")
#         t0 = time.time()
#
#         shared.is_seq2seq = False
#
#         # using AutoGPTQ
#
#         load_func_map = {
#             # 'Transformers': huggingface_loader,
#             'AutoGPTQ': AutoGPTQ_loader,
#             # 'GPTQ-for-LLaMa': GPTQ_loader,
#             # 'llama.cpp': llamacpp_loader,
#             # 'FlexGen': flexgen_loader,
#             # 'RWKV': RWKV_loader,
#             # 'ExLlama': ExLlama_loader,
#             # 'ExLlama_HF': ExLlama_HF_loader
#         }
#
#         if loader is None:
#             if shared.args.loader is not None:
#                 loader = shared.args.loader
#             else:
#                 loader = infer_loader(model_name)
#                 if loader is None:
#                     logger.error('The path to the model does not exist. Exiting.')
#                     return None, None
#
#         shared.args.loader = loader
#         output = load_func_map[loader](model_name)
#         if type(output) is tuple:
#             model, tokenizer = output
#         else:
#             model = output
#             if model is None:
#                 return None, None
#             else:
#                 tokenizer = load_tokenizer(model_name, model)
#
#         # Hijack attention with xformers
#         if any((shared.args.xformers, shared.args.sdp_attention)):
#             llama_attn_hijack.hijack_llama_attention()
#
#         logger.info(f"Loaded the model in {(time.time() - t0):.2f} seconds.\n")
#         return model, tokenizer
#
#     question = "what color is the sky?"
#
#     model, tokenizer = load_model("7bwizard")
#     tokenizer = load_tokenizer("7bwizard", None)
#     tokens = tokenizer.encode(question, add_special_tokens=True)
#     input_ids = torch.tensor([tokens])
#     print(input_ids)
#
#
# def main2():
#     name = "models/7bwizard"
#
#     text = body['prompt']
#     min_length = body.get('min_length', 0)
#     max_length = body.get('max_length', 1000)
#     top_p = body.get('top_p', 0.95)
#     top_k = body.get('top_k', 40)
#     typical_p = body.get('typical_p', 1)
#     do_sample = body.get('do_sample', True)
#     temperature = body.get('temperature', 0.6)
#     no_repeat_ngram_size = body.get('no_repeat_ngram_size', 0)
#     num_beams = body.get('num_beams', 1)
#     stopping_strings = body.get('stopping_strings', ['Human:', ])
#
#     input_ids = tokenizer.encode(text, return_tensors="pt").to(DEV)
#
#     # handle stopping strings
#     stopping_criteria_list = StoppingCriteriaList()
#     if len(stopping_strings) > 0:
#         sentinel_token_ids = [tokenizer.encode(
#             string, add_special_tokens=False, return_tensors='pt').to(DEV) for string in stopping_strings]
#         starting_idx = len(input_ids[0])
#         stopping_criteria_list.append(_SentinelTokenStoppingCriteria(
#             sentinel_token_ids, starting_idx))
#
#     with torch.no_grad():
#         generated_ids = model.generate(
#             input_ids,
#             min_length=min_length,
#             max_length=max_length,
#             top_p=top_p,
#             top_k=top_k,
#             typical_p=typical_p,
#             do_sample=do_sample,
#             temperature=temperature,
#             no_repeat_ngram_size=no_repeat_ngram_size,
#             num_beams=num_beams,
#             stopping_criteria=stopping_criteria_list,
#         )
#
#     generated_text = tokenizer.decode(
#         [el.item() for el in generated_ids[0]], skip_special_tokens=True)


def map_choice(
    text,
    index,
    token=None,
    token_logprob=None,
    top_logprobs=None,
    text_offset=None,
    finish_reason=None,
):
    """Create a choice object from model outputs."""
    choice = {
        "text": text,
        "index": index,
        "logprobs": None,
        "finish_reason": finish_reason,
    }

    # Include log probabilities of the selected and most likely tokens.
    if (
        token is not None
        and token_logprob is not None
        and top_logprobs is not None
        and text_offset is not None
    ):
        choice["logprobs"] = {
            "tokens": [token],
            "token_logprobs": [token_logprob],
            "top_logprobs": [top_logprobs],
            "text_offset": [text_offset],
        }

    return choice



class StreamTokenizer:
    """StreamTokenizer wraps around a tokenizer to support stream decoding."""

    def __init__(self, tokenizer):
        super().__init__()
        self.tokenizer = tokenizer
        self.replacement = chr(0xFFFD)
        self.buffer = []
        self.surrogates = 0
        self.start = 0
        self.end = 0

    def decode(self, token):
        """Decode token to string while handling surrogates and whitespace."""

        # <unk>, <pad> and other special tokens will be decoded into ''.
        text = self.tokenizer.decode(token, skip_special_tokens=True)

        # Handle replacement characters caused by multi-byte-pair-encoding or
        # Unicode surrogates or multi-code-point graphemes like emojis.
        if self.replacement in text:
            n = -self.surrogates if self.surrogates > 0 else len(self.buffer)
            tokens = self.buffer[n:] + [token]
            text = self.tokenizer.decode(tokens, skip_special_tokens=True)

            # Check whether the last grapheme was successfully decoded.
            if text and text[-1] != self.replacement:
                text = text.replace(self.replacement, "")
                self.surrogates = 0
            else:
                text = ""
                self.surrogates += 1
        else:
            self.surrogates = 0

        # Handle whitespace between tokens.
        tokens = self.buffer + [token]
        prefix = self.tokenizer.decode(self.buffer, skip_special_tokens=True)
        whole = self.tokenizer.decode(tokens, skip_special_tokens=True)
        if prefix + " " + text == whole:
            text = " " + text

        # Update buffer and offsets.
        self.buffer = self.buffer[-4:] + [token]
        self.start = self.end
        self.end += len(text)

        return text


class StreamModel:
    """StreamModel wraps around a language model to provide stream decoding."""

    def __init__(self, model, tokenizer):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def __call__(
        self,
        prompt,
        min_tokens=0,
        max_tokens=16,
        temperature=1.0,
        top_p=1.0,
        n=1,
        logprobs=0,
        echo=False,
        **kwargs,
    ):
        """Create a completion stream for the provided prompt."""
        if isinstance(prompt, str):
            input_ids = self.tokenize(prompt)
        elif isinstance(prompt, torch.Tensor) and prompt.dim() == 1:
            input_ids = prompt
        else:
            raise TypeError("prompt must be a string or a 1-d tensor")

        # Ensure arguments are non-negative.
        min_tokens = max(min_tokens, 0)
        max_tokens = max(max_tokens, 1)
        n = max(n, 1)
        logprobs = max(logprobs, 0)

        # Keep track of the finish reason of each sequence.
        finish_reasons = [None] * n

        # Create stateful detokenizer for each sequence.
        detokenizers = []
        for i in range(n):
            detokenizers.append(StreamTokenizer(self.tokenizer))

        # Echo prompt tokens if required.
        for token in input_ids:
            samples = self._sample(token, 0, [], []) if logprobs > 0 else {}
            for i in range(n):
                text = detokenizers[i].decode(token)
                offset = detokenizers[i].start
                if echo:
                    yield map_choice(text, i, text_offset=offset, **samples)

        generate_kwargs = {
            **dict(
                logprobs=logprobs,
                min_new_tokens=min_tokens,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            ),
            **kwargs,
        }

        # Generate completion tokens.
        for (
            tokens,
            token_logprobs,
            top_tokens,
            top_logprobs,
            status,
        ) in self.generate(
            input_ids[None, :].repeat(n, 1),
            **generate_kwargs,
        ):
            for i in range(n):
                # Check and update the finish status of the sequence.
                if finish_reasons[i]:
                    continue
                if status[i] == 0:
                    finish_reasons[i] = "stop"
                elif status[i] == -1:
                    finish_reasons[i] = "length"

                # Collect samples of the most likely tokens if required.
                samples = (
                    self._sample(
                        token=tokens[i],
                        token_logprob=token_logprobs[i],
                        top_tokens=top_tokens[i],
                        top_logprobs=top_logprobs[i],
                    )
                    if logprobs > 0
                    else {}
                )

                # Yield predicted tokens.
                text = detokenizers[i].decode(tokens[i])
                offset = detokenizers[i].start
                yield map_choice(
                    text,
                    i,
                    text_offset=offset,
                    finish_reason=finish_reasons[i],
                    **samples,
                )

    def _sample(self, token, token_logprob, top_tokens, top_logprobs):
        """Sample log probabilities of the most likely tokens."""
        token = self.tokenizer.decode(token)
        top_tokens = self.tokenizer.batch_decode(top_tokens)

        # Do not use tensor operations as arguments may be of list type.
        token_logprob = round(float(token_logprob), 8)
        top_logprobs = [round(float(p), 8) for p in top_logprobs]

        # Always include the log probability of the selected token.
        top_logprobs = dict(zip(top_tokens, top_logprobs))
        top_logprobs[token] = token_logprob

        return {
            "token": token,
            "token_logprob": token_logprob,
            "top_logprobs": top_logprobs,
        }

    def _logits_processor(self, config, input_length):
        """Set up logits processor based on the generation config."""
        processor = LogitsProcessorList()

        # Add processor for enforcing a min-length of new tokens.
        if (
            config.min_new_tokens is not None
            and config.min_new_tokens > 0
            and config.eos_token_id is not None
        ):
            processor.append(
                MinNewTokensLengthLogitsProcessor(
                    prompt_length_to_skip=input_length,
                    min_new_tokens=config.min_new_tokens,
                    eos_token_id=config.eos_token_id,
                )
            )

        # Add processor for scaling output probability distribution.
        if (
            config.temperature is not None
            and config.temperature > 0
            and config.temperature != 1.0
        ):
            processor.append(TemperatureLogitsWarper(config.temperature))

        # Add processor for nucleus sampling.
        if config.top_p is not None and config.top_p > 0 and config.top_p < 1:
            processor.append(TopPLogitsWarper(config.top_p))

        return processor

    def tokenize(self, text):
        """Tokenize a string into a tensor of token IDs."""
        batch = self.tokenizer.encode(text, return_tensors="pt")
        return batch[0].to(self.device)

    def generate(self, input_ids, logprobs=0, **kwargs):
        """Generate a stream of predicted tokens using the language model."""
        # Store the original batch size and input length.
        batch_size = input_ids.shape[0]
        input_length = input_ids.shape[-1]

        # Separate model arguments from generation config.
        config = self.model.generation_config
        print(config)
        config = copy.deepcopy(config)
        kwargs = config.update(**kwargs)
        kwargs["output_attentions"] = False
        kwargs["output_hidden_states"] = False
        kwargs["use_cache"] = config.use_cache
        # Collect special token IDs.
        pad_token_id = config.pad_token_id
        bos_token_id = config.bos_token_id
        eos_token_id = config.eos_token_id
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        if pad_token_id is None and eos_token_id is not None:
            pad_token_id = eos_token_id[0]

        # Generate from eos if no input is specified.
        if input_length == 0:
            input_ids = input_ids.new_ones((batch_size, 1)).long()
            if eos_token_id is not None:
                input_ids = input_ids * eos_token_id[0]
            input_length = 1

        # Prepare inputs for encoder-decoder models.
        if self.model.config.is_encoder_decoder:
            # Get outputs from the encoder.
            encoder = self.model.get_encoder()
            encoder_kwargs = kwargs.copy()
            encoder_kwargs.pop("use_cache", None)
            encoder_kwargs["input_ids"] = input_ids
            encoder_kwargs["return_dict"] = True
            with torch.inference_mode():
                kwargs["encoder_outputs"] = encoder(**encoder_kwargs)

            # Reinitialize inputs for the decoder.
            decoder_start_token_id = config.decoder_start_token_id
            if decoder_start_token_id is None:
                decoder_start_token_id = bos_token_id
            input_ids = input_ids.new_ones((batch_size, 1))
            input_ids = input_ids * decoder_start_token_id
            input_length = 1

        # Set up logits processor.
        processor = self._logits_processor(config, input_length)

        # Keep track of which sequences are already finished.
        unfinished = input_ids.new_ones(batch_size)
        # Start auto-regressive generation.
        while True:
            inputs = self.model.prepare_inputs_for_generation(
                input_ids, **kwargs
            )  # noqa: E501
            with torch.inference_mode():
                outputs = self.model(
                    **inputs,
                    return_dict=True,
                    output_attentions=False,
                    output_hidden_states=False,
                )

            # Pre-process the probability distribution of the next tokens.
            logits = outputs.logits[:, -1, :]
            with torch.inference_mode():
                logits = processor(input_ids, logits)
            probs = torch.nn.functional.softmax(logits, dim=-1)

            # Select deterministic or stochastic decoding strategy.
            if (config.top_p is not None and config.top_p <= 0) or (
                config.temperature is not None and config.temperature <= 0
            ):
                tokens = torch.argmax(probs, dim=-1)[:, None]
            else:
                tokens = torch.multinomial(probs, num_samples=1)

            # Collect log probabilities of the selected tokens.
            token_logprobs = torch.gather(probs, 1, tokens)
            token_logprobs = torch.log(token_logprobs + 1e-7).squeeze(1)
            tokens = tokens.squeeze(1)

            # Collect log probabilities of the most likely tokens.
            top_logprobs, top_tokens = probs.topk(logprobs)
            top_logprobs = torch.log(top_logprobs + 1e-7)

            # Finished sequences should have their next token be a padding.
            if pad_token_id is not None:
                tokens = tokens * unfinished + pad_token_id * (1 - unfinished)

            # Append selected tokens to the inputs.
            input_ids = torch.cat([input_ids, tokens[:, None]], dim=-1)

            # Extract past key values from model outputs.
            if "past_key_values" in outputs:
                kwargs["past_key_values"] = outputs.past_key_values
            elif "mems" in outputs:
                kwargs["past_key_values"] = outputs.mems
            elif "past_buckets_states" in outputs:
                kwargs["past_key_values"] = outputs.past_buckets_states

            # Mark sequences with eos tokens as finished.
            if eos_token_id is not None:
                not_eos = sum(tokens != i for i in eos_token_id)
                unfinished = unfinished.mul(not_eos.long())

            # Set status to -1 if exceeded the max length.
            status = unfinished.clone()
            if input_ids.shape[-1] - input_length >= config.max_new_tokens:
                status = 0 - status

            # Yield predictions and status.
            yield tokens, token_logprobs, top_tokens, top_logprobs, status

            # Stop when finished or exceeded the max length.
            if status.max() <= 0:
                break


def load_model(
    name_or_path,
    revision=None,
    cache_dir=None,
    load_in_8bit=False,
    load_in_4bit=False,
    local_files_only=False,
    trust_remote_code=False,
    half_precision=False,
):
    """Load a text generation model and make it stream-able."""
    kwargs = {
        "local_files_only": local_files_only,
        "trust_remote_code": trust_remote_code,
    }
    if revision:
        kwargs["revision"] = revision
    if cache_dir:
        kwargs["cache_dir"] = cache_dir
    tokenizer = AutoTokenizer.from_pretrained(name_or_path, **kwargs)

    # Set device mapping and quantization options if CUDA is available.
    if torch.cuda.is_available():
        kwargs = kwargs.copy()
        kwargs["device_map"] = "auto"
        kwargs["load_in_8bit"] = load_in_8bit
        kwargs["load_in_4bit"] = load_in_4bit

        # Cast all parameters to float16 if quantization is enabled.
        if half_precision or load_in_8bit or load_in_4bit:
            kwargs["torch_dtype"] = torch.float16

    # Support both decoder-only and encoder-decoder models.
    try:
        model = AutoModelForCausalLM.from_pretrained(name_or_path, **kwargs)
    except ValueError:
        model = AutoModelForSeq2SeqLM.from_pretrained(name_or_path, **kwargs)

    # Check if the model has text generation capabilities.
    if not model.can_generate():
        raise TypeError(f"{name_or_path} is not a text generation model")

    return StreamModel(model.eval(), tokenizer)

def test_speed():
    model_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
    model_dir = os.path.join(model_dir, "celeryr/t5-model")
    # model_dir = os.path.join(model_dir, "ai_test/char_test/models/7bwizard")
    # tokenizer = T5Tokenizer.from_pretrained(model_dir)
    # model = T5ForConditionalGeneration.from_pretrained(model_dir)
    # config = GenerationConfig(
    #     max_new_tokens=100,
    #     min_new_tokens=10,
    #     min_tokens=0,
    #     max_tokens=16,
    #     temperature=1.0,
    #     top_p=1.0,
    #     n=1,
    # )
    # print("model loaded")
    # text = "once upon a time"
    # input_ids = tokenizer(text, return_tensors="pt").input_ids
    # outputs = model.generate(input_ids, generation_config=config)
    # output_text = tokenizer.decode(outputs[0])
    # print(output_text)
    model = load_model(model_dir)
    print("model loaded")
    text = "how big are the oceans?"
    text_out = ""
    for choice in model(text,
                        max_new_tokens=200,
                        # min_new_tokens=10,
                        do_sample= True,
                        temperature= 0,
                        top_p= 0.9,
                        typical_p= 1,
                        repetition_penalty= 1.15,
                        encoder_repetition_penalty= 1,
                        top_k= 20,
                        min_length= 0,
                        no_repeat_ngram_size= 0,
                        num_beams= 1,
                        penalty_alpha= 0,
                        length_penalty= 1,
                        early_stopping= False,
                        ):
        text_out += choice["text"]
        print(choice["text"])
    print(text_out)

    #
    # next_token_id = outputs[:, -1]
    # next_token = tokenizer.decode(next_token_id)
    # print(next_token)
    # output_text = tokenizer.decode(outputs[0])
    # print(output_text)
    # output_text = output_text.replace("<pad>", "").replace("</s>", "")
    # print(output_text)
    pass

if __name__ == '__main__':
    # main()
    # main2()
    test_speed()