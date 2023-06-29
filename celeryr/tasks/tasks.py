import os
import time

from celery import Celery
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig

celery = Celery("tasks")
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


model = None
tokenize = None
config = None
e = time.time()

def load_model():
    s = time.time()
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_name = os.path.join(model_dir, 'models-google-flan-t5-small')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = GenerationConfig(max_new_tokens=50)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    print(e - s)
    print("model loaded")
    return model, tokenizer, config

@celery.task(name="tasks.create_task", time_limit=60)
def create_task(text):
    print(f"input text {text}")
    global model, tokenizer, config
    if model is None:
        model, tokenizer, config = load_model()
    output = "Ask something else"
    try:
        tokens = tokenizer(text, return_tensors="pt")
        outputs = model.generate(**tokens, generation_config=config)
        sent = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        output = sent[0]
    except Exception as e:
        print(e)
        pass
    print(f"ouput text {output}")
    return output