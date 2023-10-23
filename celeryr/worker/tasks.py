import os
import time

from celery import Celery
from sqlalchemy import and_
# from worker.database import get_session, Item, SessionLocal
from transformers import T5Tokenizer, T5ForConditionalGeneration

from worker.database import get_session, DBMessage

# Python 3.10.9
DATABASE_URI = os.environ.get("REDIS_BROKER_URL", 'redis://localhost:6379/0')

celery_app = Celery(
    'tasks',
    broker=DATABASE_URI,  # Replace with your Redis server configuration
    backend=DATABASE_URI,  # Replace with your Redis server configuration
)

model = None
tokenizer = None

MESSAGES_SIZE = 5

# size is in tokens
MAX_OUTPUT_LENGTH = 50
MAX_INPUT_LENGTH = 512


def load_model():
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(model_dir, "t5-model")
    print(model_dir)
    print(os.listdir(model_dir))
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model = T5ForConditionalGeneration.from_pretrained(model_dir)
    return model, tokenizer

@celery_app.on_after_configure.connect
def setup_model(sender, **kwargs):
    print(sender)
    # global model
    # global tokenizer
    # print("start loading")
    # s = time.time()
    # model, tokenizer = load_model()
    # e = time.time()
    # print(f"models loaded: {e - s}")
    # print("use model")
    # s = time.time()
    # res = use_model("what color is the sky")
    # print(res)
    # e = time.time()
    # print(f"model used: {e - s}")



def get_chat(chat_id):
    with get_session() as session:
        messages = session.query(DBMessage).filter(and_(
            DBMessage.chat_id == chat_id,
            DBMessage.deleted == False
        )).all()[-MESSAGES_SIZE:]
    return messages

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


def format_chat(messages) -> str:
    text = ""
    for m in messages:
        if m.type == "user":
            text += f"User: {m.message_en}\n "
        else:
            text += f"Vambola: {m.message_en}\n "
    text += "Vambola: "
    return text

@celery_app.task(name="get_message", time_limit=60)
def simple_task(chat_id):
    messages = get_chat(chat_id)
    text = format_chat(messages)
    print(f"input: {[text]}")
    res = use_model(text)
    print(f"output: {res}")
    return res

@celery_app.task(name="test")
def test():
    print("hi")


