import os

from transformers import T5Tokenizer, T5ForConditionalGeneration

# size is in tokens
MAX_OUTPUT_LENGTH = 50
MAX_INPUT_LENGTH = 512

model = None
tokenizer = None


def load_model():
    global model
    global tokenizer
    model_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(model_dir, "t5-model")
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model = T5ForConditionalGeneration.from_pretrained(model_dir)


def use_model(prompt):
    global model  # Use the global model variable
    global tokenizer  # Use the global tokenizer variable
    # model, tokenizer = load_model()
    try:
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        # if gets too long cut out front
        if input_ids.size(1) > MAX_INPUT_LENGTH:
            input_ids = input_ids[:, -MAX_INPUT_LENGTH:]
        outputs = model.generate(input_ids,
                                 max_new_tokens=MAX_OUTPUT_LENGTH,
                                 temperature=0.75,
                                 do_sample=True,
                                 top_p=0.9,
                                 typical_p=1,
                                 repetition_penalty=1.15,
                                 encoder_repetition_penalty=1,
                                 top_k=20,
                                 min_length=0,
                                 no_repeat_ngram_size=0,
                                 num_beams=1,
                                 penalty_alpha=0,
                                 length_penalty=1,
                                 early_stopping=False,
                                 )
        output_text = tokenizer.decode(outputs[0])
        output_text = output_text.replace("<pad>", "").replace("</s>", "")
    except Exception as e:
        print(e)
        return None
    return output_text
