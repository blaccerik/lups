import os
import time

from celery import Celery
from deep_translator import GoogleTranslator
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig

celery = Celery("tasks")
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

s = time.time()
model = None
tokenize = None
config = None
e = time.time()
print(e - s)
print("model loaded")

def load_model():
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_name = os.path.join(model_dir, 'models-google-flan-t5-small')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = GenerationConfig(max_new_tokens=50)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer, config

@celery.task(name="tasks.create_task", time_limit=60)
def create_task(text):
    print(f"input text {text}")
    global model, tokenizer, config
    if model is None:
        model, tokenizer, config = load_model()
    output_text_en = "Ask something else"
    output_text_ee = "Küsi midagi muud"
    try:
        input_text_en = GoogleTranslator(source='et', target='en').translate(text)
        tokens = tokenizer(input_text_en, return_tensors="pt")
        outputs = model.generate(**tokens, generation_config=config)
        sent = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        output_text_en = sent[0]
        output_text_ee = GoogleTranslator(source='en', target='et').translate(output_text_en)
    except Exception as e:
        print(e)
        pass

    print(f"ouput text {output_text_ee} {output_text_en}")
    return output_text_ee, output_text_en


# @celery.task(name="tasks.check_unload_model", time_limit=10)
# def check_unload_model():
#     print("unload fun")
#     last_used = int(redis_client.get('last_used'))
#     print(int(time.time()) - last_used)
#     if int(time.time()) - last_used >= COUNTDOWN_DURATION:
#         global tokenizer, model, config
#         del tokenizer
#         del model
#         del config
#         print("unloaded")
#     print("unload fun end")
