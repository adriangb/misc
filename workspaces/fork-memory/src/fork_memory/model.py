from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline


def load_model() -> Model:
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    id2label = {0: "positive", 1: "negative"}
    model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=2, id2label=id2label)
    pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)
    return pipe
