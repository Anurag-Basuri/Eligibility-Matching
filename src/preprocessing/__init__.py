from .text_cleaner import clean_text
from .tokenizer import tokenize

def preprocess(text: str) -> str:
    text = clean_text(text)
    text = tokenize(text)
    return text
