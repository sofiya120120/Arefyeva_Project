import torch
from transformers import pipeline
from deep_translator import GoogleTranslator
from config import MODEL_T5

device = 0 if torch.cuda.is_available() else -1

qg_pipeline = pipeline(
    "text2text-generation",
    model=MODEL_T5,
    device=device,
    tokenizer=MODEL_T5,
    use_fast=False
)


to_en = GoogleTranslator(source="auto", target="en")
to_ru = GoogleTranslator(source="en", target="ru")
