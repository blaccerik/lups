import heapq
import os
import re
import sys
import time

from flaskr.db_models.models import Session, Message
import nltk
import numpy as np
from nltk import WordNetLemmatizer, word_tokenize
nltk.download('punkt')
nltk.download('wordnet')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import and_
import torch
from transformers import AutoTokenizer, GenerationConfig, AutoModelForSeq2SeqLM, T5Tokenizer, \
    T5ForConditionalGeneration, GPT2Tokenizer, GPT2LMHeadModel, pipeline


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


# Define global variable to store the loaded model
model = None
tokenizer = None
config = None
vectorizer = None
vectorized_data = None
raw = None


def read_file(name):
    with open(name, "r", encoding="utf-8") as f:
        return f.readlines()


def remove_brackets(string):
    # Remove square brackets and their contents
    pattern = r'\[[^\]]*\]'
    string = re.sub(pattern, '', string)
    return string


def is_sentence(string):
    punctuation_marks = ['.', '?', '!']
    if string.strip().endswith(tuple(punctuation_marks)):
        return True
    else:
        return False


def clean(all_data, lemmatizer, string: str):
    # Remove square brackets and their contents
    string = remove_brackets(string)

    # Tokenize the normalized string into sentences
    sentences = nltk.sent_tokenize(string)
    for s in sentences:
        if " " not in s:
            continue
        if not is_sentence(s):
            continue
        normalized_string = clean_string(s, lemmatizer)
        all_data.append((s, normalized_string))


def clean_string(s, lemmatizer):
    tokens = word_tokenize(s)
    normalized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    normalized_string = ' '.join(normalized_tokens)
    return normalized_string


def load_model():
    global model, tokenizer, config, vectorizer, vectorized_data, raw
    s = time.time()
    # model_dir = os.path.dirname(os.path.abspath(__file__))
    # model_name = os.path.join(model_dir, 'models-google-flan-t5-small')

    name = "google/flan-t5-xl"

    tokenizer = T5Tokenizer.from_pretrained(name)
    model = T5ForConditionalGeneration.from_pretrained(name)
    config = GenerationConfig(max_new_tokens=100, min_new_tokens=50)

    # Lemmatize and lowercase the string
    lemmatizer = WordNetLemmatizer()

    all_data = []
    # read file

    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")
    for i in os.listdir(dir):
        lines = read_file(os.path.join(dir, i))
        for line in lines:
            clean(all_data, lemmatizer, line)
    raw = [a for a, b in all_data]
    cleaned = [b for a, b in all_data]

    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the vectorizer on the data
    vectorized_data = vectorizer.fit_transform(cleaned)

    e = time.time()
    print(f"models loaded: {e - s}")


def get_facts(text: str):
    global vectorizer, vectorized_data, raw
    threshold = 0.2
    num_strings = 10

    # Transform the question into a vector
    vectorized_question = vectorizer.transform([text])

    # Compute the cosine similarity between the question and each string
    similarities = cosine_similarity(vectorized_question, vectorized_data)[0]

    # Sort the indices based on the similarity scores
    relevant_indices = np.where(similarities >= threshold)[0]
    top_indices = relevant_indices[np.argsort(similarities[relevant_indices])][::-1][:num_strings]

    # Get the most relevant strings from the list
    top_strings = [raw[i] for i in top_indices]
    return top_strings


def generate_prompt(facts, chat):
    # Create markers for long-term facts and chat history
    long_term_facts_marker = "The following are facts:"
    chat_history_marker = "The following is the chat history:"
    # # Concatenate long-term facts and chat history with markers
    prompt = f"{long_term_facts_marker}\n" + "\n".join(facts) + \
             f"\n\n{chat_history_marker}\n" + "\n".join(chat)
    prompt += f"\nVambola: "
    return prompt

def format_chat(facts, messages):
    long_term_facts_marker = "The following are facts:\n"
    chat_history_marker = "\nThe following is the chat history:\n"
    prompt = ""
    prompt += long_term_facts_marker
    prompt += "\n".join(facts)
    prompt += chat_history_marker
    for m in messages:
        if m.type == "user":
            prompt += f"User: {m.message_en}\n"
        else:
            prompt += f"Vambola: {m.message_en}\n"
    prompt += "Vambola: "
    return prompt

def create_task(chat_id: int, question_id: int):
    global model, tokenizer, config
    # print(f"chat id: {chat_id}")
    #
    # history_size = 5
    #
    # # Retrieve the last 10 messages from the specified chat
    # with Session() as session:
    #     messages = session.query(Message).filter(and_(
    #         Message.chat_id == chat_id,
    #         Message.deleted == False
    #     )).all()[-10:]
    #
    # # user cleared
    # print(len(messages))
    # if len(messages) == 0:
    #     return False, "no messages"
    #
    # question = None
    # # clean text
    # for m in messages:
    #     if m.id == question_id:
    #         question = m.message_en
    # print(f"question {question}")
    # if question is None:
    #     return False, "no question"
    #
    # # load facts
    # facts = get_facts(question)
    # print(f"facts: {len(facts)}")
    #
    # prompt = format_chat(facts, messages)
    # output = "Ask something else"
    # print(prompt)

    prompt = """The following are facts:
    
Ekre is bad.
Lüps is good.
Vambola hates russians.
Vambola is an AI chat bot

The following is the chat history:

User: Hello.
Vambola: Hi.
User: Who are you?
Vambola: """
    # tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")
    # model = GPT2LMHeadModel.from_pretrained("EleutherAI/gpt-neo-1.3B")

    # generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
    # a = generator("EleutherAI has", do_sample=True, min_length=50)
    # print(a)
    # generate_text = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True,
    #                          device_map="cpu")
    # res = generate_text("Explain to me the difference between nuclear fission and fusion.")
    # print(res[0]["generated_text"])

    # tokens = tokenizer.encode(prompt, return_tensors="pt")
    # outputs = model.generate(tokens, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    #
    # response = tokenizer.decode(outputs[:, tokens.shape[-1]:][0], skip_special_tokens=True)
    # print(response)

    # from transformers import pipeline, set_seed
    # generator = pipeline('text-generation', model='distilgpt2')
    # set_seed(42)
    # a = generator("What should I do?", max_new_tokens=100)
    # print(a)

    chat_history = """
    User: What is the capital of France?
    """

    prompt = chat_history

    generator = pipeline('text-generation', model='distilgpt2')
    output = generator(prompt, max_length=50, num_return_sequences=1, max_new_tokens=100)

    response = output
    print(response)

if __name__ == '__main__':
    print(create_task(4, 116))