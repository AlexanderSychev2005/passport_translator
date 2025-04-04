import nltk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from math import pi
from datasets import load_dataset
import evaluate
import os
from deepl import Translator
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from nltk.translate.meteor_score import meteor_score

nltk.download("wordnet")
matplotlib.use('TkAgg')

# def translate_marian(sentences, model_name='Helsinki-NLP/opus-mt-en-uk'):
#     tokenizer = MarianTokenizer.from_pretrained(model_name)
#     model = MarianMTModel.from_pretrained(model_name)
#     inputs = tokenizer(sentences, return_tensors="pt", padding=True, truncation=True)
#     outputs = model.generate(**inputs)
#     return [tokenizer.decode(t, skip_special_tokens=True) for t in outputs]


def translate_google(sentences, src="en", dest="uk"):
    """
    Method for translating sentences using Google Translate
    :param sentences: a list containing sentences
    :param src: language we translate from
    :param dest: language we translate to
    :return: list of translated sentences
    """
    translator = GoogleTranslator()
    results = []
    for sentence in sentences:
        result = translator.translate(sentence, src=src, dest=dest)
        results.append(result)
    return results


dataset = load_dataset("LT3/nfr_bt_nmt_english-ukrainian", split="validation")
small_sample = dataset.train_test_split(test_size=0.01)["test"]

load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

translator_deepl = Translator(DEEPL_API_KEY)

english_sentences = small_sample["english"]
ukrainian_sentences = small_sample["ukrainian"]

translations_deepl = [
    translator_deepl.translate_text(sentence, target_lang="UK").text
    for sentence in english_sentences
]
translations_google = translate_google(english_sentences)
# translations_marian = translate_marian(english_sentences)
bleu = evaluate.load("bleu")

references = [[ref] for ref in ukrainian_sentences]
bleu_deepl = bleu.compute(predictions=translations_deepl, references=references)["bleu"]
bleu_google = bleu.compute(predictions=translations_google, references=references)[
    "bleu"
]
# bleu_marian = bleu.compute(predictions=translations_marian, references=references)['bleu']


print(f"BLEU score deepl: {bleu_deepl:.2f}")
print(f"BLEU score google: {bleu_google:.2f}")
# print(f"BLEU score marian: {bleu_marian}")


score_deepl = meteor_score(references, translations_deepl)
score_google = meteor_score(references, translations_google)
print(f"METEOR Score Deepl: {score_deepl:.2f}")
print(f"METEOR Score Google: {score_google:.2f}")


bertscore = evaluate.load("bertscore")

bertscore_deepl = bertscore.compute(
    predictions=translations_deepl, references=ukrainian_sentences, lang="uk"
)
bertscore_google = bertscore.compute(
    predictions=translations_google, references=ukrainian_sentences, lang="uk"
)

print(f"BERTScore Deepl (F1): {np.mean(bertscore_deepl['f1']):.2f}")
print(f"BERTScore Google (F1): {np.mean(bertscore_google['f1']):.2f}")

deepl_scores = [bleu_deepl, score_deepl, np.mean(bertscore_deepl["f1"])]
google_scores = [bleu_google, score_google, np.mean(bertscore_google["f1"])]

metrics = {
    "DeepL": deepl_scores,
    "Google": google_scores,
}

labels = ['BLEU', 'METEOR', 'BERTScore']
n = len(labels)


angles = [i * 2 * pi / n for i in range(n)]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

values_deepl = metrics['DeepL']
values_deepl += values_deepl[:1]
ax.plot(angles, values_deepl, linewidth=2, linestyle='solid', label='DeepL')
ax.fill(angles, values_deepl, 'b', alpha=0.1)

values_google = metrics['Google']
values_google += values_google[:1]
ax.plot(angles, values_google, linewidth=2, linestyle='solid', label='Google')
ax.fill(angles, values_google, 'r', alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)

plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

plt.title("Translation metrics comparison")
plt.show()