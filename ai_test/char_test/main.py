import re
import time
import torch
import logging

logging.basicConfig(level=logging.INFO)
from pathlib import Path
import modules.shared as shared
import hashlib

def main():

    logger = logging.getLogger("main")
    logger.info("logger test")

    def AutoGPTQ_loader(model_name):
        import modules.AutoGPTQ_loader

        return modules.AutoGPTQ_loader.load_quantized(model_name)

    def load_tokenizer(model_name, model):
        tokenizer = None
        path_to_model = Path(f"{shared.args.model_dir}/{model_name}/")
        if any(s in model_name.lower() for s in ['gpt-4chan', 'gpt4chan']) and Path(
                f"{shared.args.model_dir}/gpt-j-6B/").exists():
            tokenizer = AutoTokenizer.from_pretrained(Path(f"{shared.args.model_dir}/gpt-j-6B/"))
        elif path_to_model.exists():
            tokenizer = AutoTokenizer.from_pretrained(
                path_to_model,
                trust_remote_code=shared.args.trust_remote_code,
                use_fast=False
            )

        if tokenizer.__class__.__name__ == 'LlamaTokenizer':
            pairs = [
                ['tokenizer_config.json', '516c6167c884793a738c440e29ccb80c15e1493ffc965affc69a1a8ddef4572a'],
                ['special_tokens_map.json', 'ff3b4a612c4e447acb02d40071bddd989fe0da87eb5b7fe0dbadfc4f74de7531']
            ]

            for pair in pairs:
                p = path_to_model / pair[0]
                if p.exists():
                    with open(p, "rb") as f:
                        bytes = f.read()

                    file_hash = hashlib.sha256(bytes).hexdigest()
                    if file_hash != pair[1]:
                        logger.warning(
                            f"{p} is different from the original LlamaTokenizer file. It is either customized or outdated.")

        return tokenizer

    def get_model_settings_from_yamls(model):
        settings = shared.model_config
        model_settings = {}
        for pat in settings:
            if re.match(pat.lower(), model.lower()):
                for k in settings[pat]:
                    model_settings[k] = settings[pat][k]

        return model_settings

    def infer_loader(model_name):
        path_to_model = Path(f'{shared.args.model_dir}/{model_name}')
        model_settings = get_model_settings_from_yamls(model_name)
        if not path_to_model.exists():
            loader = None
        elif Path(f'{shared.args.model_dir}/{model_name}/quantize_config.json').exists() or (
                'wbits' in model_settings and type(model_settings['wbits']) is int and model_settings['wbits'] > 0):
            loader = 'AutoGPTQ'
        elif len(list(path_to_model.glob('*ggml*.bin'))) > 0:
            loader = 'llama.cpp'
        elif re.match('.*ggml.*\.bin', model_name.lower()):
            loader = 'llama.cpp'
        elif re.match('.*rwkv.*\.pth', model_name.lower()):
            loader = 'RWKV'
        elif shared.args.flexgen:
            loader = 'FlexGen'
        else:
            loader = 'Transformers'

        return loader

    def load_model(model_name, loader=None):
        logger.info(f"Loading {model_name}...")
        t0 = time.time()

        shared.is_seq2seq = False

        # using AutoGPTQ

        load_func_map = {
            # 'Transformers': huggingface_loader,
            'AutoGPTQ': AutoGPTQ_loader,
            # 'GPTQ-for-LLaMa': GPTQ_loader,
            # 'llama.cpp': llamacpp_loader,
            # 'FlexGen': flexgen_loader,
            # 'RWKV': RWKV_loader,
            # 'ExLlama': ExLlama_loader,
            # 'ExLlama_HF': ExLlama_HF_loader
        }

        if loader is None:
            if shared.args.loader is not None:
                loader = shared.args.loader
            else:
                loader = infer_loader(model_name)
                if loader is None:
                    logger.error('The path to the model does not exist. Exiting.')
                    return None, None

        shared.args.loader = loader
        output = load_func_map[loader](model_name)
        if type(output) is tuple:
            model, tokenizer = output
        else:
            model = output
            if model is None:
                return None, None
            else:
                tokenizer = load_tokenizer(model_name, model)

        # Hijack attention with xformers
        if any((shared.args.xformers, shared.args.sdp_attention)):
            llama_attn_hijack.hijack_llama_attention()

        logger.info(f"Loaded the model in {(time.time() - t0):.2f} seconds.\n")
        return model, tokenizer

    question = "what color is the sky?"

    model, tokenizer = load_model("7bwizard")
    tokenizer = load_tokenizer("7bwizard", None)
    tokens = tokenizer.encode(question, add_special_tokens=True)
    input_ids = torch.tensor([tokens])
    print(input_ids)


def main2():
    name = "models/7bwizard"

    text = body['prompt']
    min_length = body.get('min_length', 0)
    max_length = body.get('max_length', 1000)
    top_p = body.get('top_p', 0.95)
    top_k = body.get('top_k', 40)
    typical_p = body.get('typical_p', 1)
    do_sample = body.get('do_sample', True)
    temperature = body.get('temperature', 0.6)
    no_repeat_ngram_size = body.get('no_repeat_ngram_size', 0)
    num_beams = body.get('num_beams', 1)
    stopping_strings = body.get('stopping_strings', ['Human:', ])

    input_ids = tokenizer.encode(text, return_tensors="pt").to(DEV)

    # handle stopping strings
    stopping_criteria_list = StoppingCriteriaList()
    if len(stopping_strings) > 0:
        sentinel_token_ids = [tokenizer.encode(
            string, add_special_tokens=False, return_tensors='pt').to(DEV) for string in stopping_strings]
        starting_idx = len(input_ids[0])
        stopping_criteria_list.append(_SentinelTokenStoppingCriteria(
            sentinel_token_ids, starting_idx))

    with torch.no_grad():
        generated_ids = model.generate(
            input_ids,
            min_length=min_length,
            max_length=max_length,
            top_p=top_p,
            top_k=top_k,
            typical_p=typical_p,
            do_sample=do_sample,
            temperature=temperature,
            no_repeat_ngram_size=no_repeat_ngram_size,
            num_beams=num_beams,
            stopping_criteria=stopping_criteria_list,
        )

    generated_text = tokenizer.decode(
        [el.item() for el in generated_ids[0]], skip_special_tokens=True)


if __name__ == '__main__':
    main()
    main2()