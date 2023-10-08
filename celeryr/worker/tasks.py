import os
import time

from celery import Celery
# from worker.database import get_session, Item, SessionLocal
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Python 3.10.9
DATABASE_URI = os.environ.get("REDIS_BROKER_URL", 'redis://localhost:6379/0')

celery_app = Celery(
    'tasks',
    broker=DATABASE_URI,  # Replace with your Redis server configuration
    backend=DATABASE_URI,  # Replace with your Redis server configuration
)

model = None
tokenizer = None

# size is in tokens
MAX_OUTPUT_LENGTH = 50
MAX_INPUT_LENGTH = 512


@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    global model
    global tokenizer
    s = time.time()
    model_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(model_dir, "t5-model")
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model = T5ForConditionalGeneration.from_pretrained(model_dir)
    e = time.time()
    print(f"models loaded: {e - s}")


def use_model(prompt):
    global model, tokenizer
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


@celery_app.task(name="simple_task")
def simple_task(chat_id):
    res = use_model("hello")
    return res
