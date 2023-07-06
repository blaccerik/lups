import torch
import transformers
from transformers import AutoTokenizer, LlamaConfig, LlamaForCausalLM
from utils import find_layers
import quant

DEV = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(DEV)
# Update to whichever GPTQ model you want to load
MODEL_NAME = r'C:\Users\erik\PycharmProjects\lups\ai_test\char_test\models\7bwizard'
# Update the model weight that you want to load for inference.
MODEL_PATH = r'C:\Users\erik\PycharmProjects\lups\ai_test\char_test\models\7bwizard\wizardLM-7B-GPTQ-4bit.compat.no-act-order.safetensors'


def load_quant(model, checkpoint, wbits, groupsize=-1, fused_mlp=True, eval=True, warmup_autotune=True):
    config = LlamaConfig.from_pretrained(model)

    def noop(*args, **kwargs):
        pass

    torch.nn.init.kaiming_uniform_ = noop
    torch.nn.init.uniform_ = noop
    torch.nn.init.normal_ = noop

    torch.set_default_dtype(torch.half)
    transformers.modeling_utils._init_weights = False
    torch.set_default_dtype(torch.half)
    model = LlamaForCausalLM(config)
    torch.set_default_dtype(torch.float)
    if eval:
        model = model.eval()
    layers = find_layers(model)
    for name in ['lm_head']:
        if name in layers:
            del layers[name]
    quant.make_quant_linear(model, layers, wbits, groupsize)

    del layers

    print('Loading model ...')
    if checkpoint.endswith('.safetensors'):
        from safetensors.torch import load_file as safe_load
        model.load_state_dict(safe_load(checkpoint), strict=False)
    else:
        model.load_state_dict(torch.load(checkpoint), strict=False)

    if eval:
        quant.make_quant_attn(model)
        quant.make_quant_norm(model)
        if fused_mlp:
            quant.make_fused_mlp(model)
    if warmup_autotune:
        quant.autotune_warmup_linear(model, transpose=not (eval))
        if eval and fused_mlp:
            quant.autotune_warmup_fused(model)
    model.seqlen = 2048

    return model


class SingletonModelTokenizer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonModelTokenizer, cls).__new__(cls)
            cls._instance.model = load_quant(MODEL_NAME, MODEL_PATH, 4, 128)
            cls._instance.model.to(DEV)
            cls._instance.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        return cls._instance


singleton = SingletonModelTokenizer()
model = singleton.model
tokenizer = singleton.tokenizer


def main():
    body = {}

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

    response = json.dumps({'results': [{'text': generated_text}]})


if __name__ == '__main__':
    # main()
    print("done")
