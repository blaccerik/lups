import heapq
import os
import time
from functools import lru_cache

import redis
from celery import Celery
from sqlalchemy import and_
from transformers import T5Tokenizer, T5ForConditionalGeneration
# try to load database models
from worker.models import Session, Message

# Initialize the Redis client
redis_client = redis.Redis.from_url("redis://redis:6379/0", decode_responses=True)

celery = Celery("tasks")
celery.conf.broker_url = "redis://localhost:6379"
celery.conf.result_backend = "redis://localhost:6379"

MESSAGES_SIZE = 5
FACTS_SIZE = 3
FACT_THRESHOLD = 0.2

# size is in tokens
MAX_OUTPUT_LENGTH = 50
MAX_INPUT_LENGTH = 512


@lru_cache(maxsize=1)
def load_model():
    s = time.time()
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(model_dir, "t5-model/")
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model = T5ForConditionalGeneration.from_pretrained(model_dir)
    e = time.time()
    print(f"models loaded: {e - s}")
    return model, tokenizer


def format_chat(messages) -> str:
    # long_term_facts_marker = "\nThe following are facts:\n\n"
    # chat_history_marker = "\nThe following is the chat history:\n\n"

    text = ""
    # text += long_term_facts_marker
    # for f in facts:
    #     text += f + "\n"
    # text += chat_history_marker
    for m in messages:
        if m.type == "user":
            text += f"User: {m.message_en}\n"
        else:
            text += f"Vambola: {m.message_en}\n"
    text += "Vambola: "
    return text


def get_messages(chat_id, question_id):
    # Retrieve the last 10 messages from the specified chat
    with Session() as session:
        messages = session.query(Message).filter(and_(
            Message.chat_id == chat_id,
            Message.deleted == False
        )).all()[-MESSAGES_SIZE:]

    question = None
    for m in messages:
        if m.id == question_id:
            question = m.message_en
            break
    return messages, question


@celery.task(name="my_task", time_limit=60)
def create_task(chat_id: int, question_id: int):
    # load stuff if needed
    model, tokenizer = load_model()

    print(f"chat id: {chat_id}")
    messages, question = get_messages(chat_id, question_id)
    # user cleared
    if len(messages) == 0:
        return False, "no messages"
    # no question
    if question is None:
        return False, "no question"

    # # load facts
    # facts = fr.get_facts(question)

    # make prompt
    prompt = format_chat(messages)
    print([prompt])
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
        return False, "model error"
    return True, output_text
