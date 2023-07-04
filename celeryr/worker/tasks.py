import heapq
import os
import re
import time
from functools import lru_cache

import nltk
import numpy as np
from celery import Celery
from nltk import WordNetLemmatizer, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import and_
from transformers import T5Tokenizer, T5ForConditionalGeneration
# try to load database models
from worker.models import Session, Message

celery = Celery("tasks")
celery.conf.broker_url = "redis://localhost:6379"
celery.conf.result_backend = "redis://localhost:6379"

MESSAGES_SIZE = 5
FACTS_SIZE = 3
FACT_THRESHOLD = 0.2
MAX_OUTPUT_LENGTH = 100


class FixedSizeList:
    def __init__(self, size):
        self.size = size
        self.data = []

    def push(self, score, item):
        if len(self.data) < self.size:
            heapq.heappush(self.data, (score, item))
        else:
            heapq.heappushpop(self.data, (score, item))

    def get_list(self):
        return sorted(self.data)


class FactRetrieve:
    def __init__(self):
        # Lemmatize and lowercase the string
        lemmatizer = WordNetLemmatizer()

        all_data = []

        # read file
        dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
        for i in os.listdir(dir):
            lines = self.read_file(os.path.join(dir, i))
            for line in lines:
                self.clean(all_data, lemmatizer, line)
        self.raw = [a for a, b in all_data]
        cleaned = [b for a, b in all_data]

        # Create a TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer()

        # Fit and transform the vectorizer on the data
        self.vectorized_data = self.vectorizer.fit_transform(cleaned)

    def clean(self, all_data, lemmatizer, string: str):
        # Remove square brackets and their contents
        string = self.remove_brackets(string)

        # Tokenize the normalized string into sentences
        sentences = nltk.sent_tokenize(string)
        for s in sentences:
            if " " not in s:
                continue
            if not self.is_sentence(s):
                continue
            normalized_string = self.clean_string(s, lemmatizer)
            all_data.append((s, normalized_string))

    def clean_string(self, s, lemmatizer):
        tokens = word_tokenize(s)
        normalized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
        normalized_string = ' '.join(normalized_tokens)
        return normalized_string

    def read_file(self, name):
        with open(name, "r", encoding="utf-8") as f:
            return f.readlines()

    def remove_brackets(self, string):
        # Remove square brackets and their contents
        pattern = r'\[[^\]]*\]'
        string = re.sub(pattern, '', string)
        return string

    def is_sentence(self, string):
        punctuation_marks = ['.', '?', '!']
        if string.strip().endswith(tuple(punctuation_marks)):
            return True
        else:
            return False

    def get_facts(self, text: str):

        # Transform the question into a vector
        vectorized_question = self.vectorizer.transform([text])

        # Compute the cosine similarity between the question and each string
        similarities = cosine_similarity(vectorized_question, self.vectorized_data)[0]

        # Sort the indices based on the similarity scores
        relevant_indices = np.where(similarities >= FACT_THRESHOLD)[0]
        top_indices = relevant_indices[np.argsort(similarities[relevant_indices])][::-1][:FACTS_SIZE]

        # Get the most relevant strings from the list
        top_strings = [self.raw[i] for i in top_indices]
        return top_strings


@lru_cache(maxsize=1)
def load_model():
    s = time.time()
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(model_dir, "t5-model/")
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model = T5ForConditionalGeneration.from_pretrained(model_dir)
    fr = FactRetrieve()
    e = time.time()
    print(f"models loaded: {e - s}")
    return model, tokenizer, fr


def format_chat(facts, messages) -> str:

    long_term_facts_marker = "\nThe following are facts:\n\n"
    chat_history_marker = "\nThe following is the chat history:\n\n"

    text = ""
    text += long_term_facts_marker
    for f in facts:
        text += f + "\n"
    text += chat_history_marker
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
    model, tokenizer, fr = load_model()

    print(f"chat id: {chat_id}")
    messages, question = get_messages(chat_id, question_id)
    # user cleared
    if len(messages) == 0:
        return False, "no messages"
    # no question
    if question is None:
        return False, "no question"

    # load facts
    facts = fr.get_facts(question)

    # make prompt
    prompt = format_chat(facts, messages)
    # print(prompt)
    try:
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        outputs = model.generate(input_ids, max_new_tokens=MAX_OUTPUT_LENGTH)
        output_text = tokenizer.decode(outputs[0])
        output_text = output_text.replace("<pad>", "").replace("</s>", "")
    except Exception as e:
        print(e)
        return False, "model error"
    return True, output_text
