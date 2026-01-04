import spacy

nlp = spacy.load("en_core_web_sm")

def tokenize(text: str) -> str:
    doc = nlp(text)
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct and len(token) > 2
    ]
    return " ".join(tokens)
