#!flask/bin/python
import os
import spacy
import re
import sys

from flask import Flask, render_template, request
from database_connector import write_article_to_db

app = Flask(__name__)
app._static_folder = os.path.abspath("templates/static/")
nlp = spacy.load("en_core_web_sm")
nlp.tokenizer.rules = {key: value for key, value in nlp.tokenizer.rules.items() if
                       "'" not in key and "’" not in key and "‘" not in key}

TEXT = 'TEXT'
advcl = 'advcl'
ADP = 'ADP'
PUNCT = 'PUNCT'
ROOT = 'ROOT'
AUX = 'AUX'
CONJ = 'CONJ'
SCONJ = 'SCONJ'
CCONJ = 'CCONJ'
neg = 'neg'
prep = 'prep'
advmod = 'advmod'

NO_SPLIT_LIMIT = 6
MIN_PHRASE_LENGTH = 4
MAX_PHRASE_LENGTH = 8


@app.route('/')
def output():
    # serve index template
    return render_template('index.html')


@app.route('/receiver', methods=['GET', 'POST'])
def process_request():
    data = request.get_json()
    if request.method == 'POST' and request.is_json:
        request_json = request.get_json()

        if TEXT in request_json.keys():
            processed_text = process_input(request_json[TEXT])
            return processed_text, 200
    return 'Method Not Allowed', 405


def process_input(input_text):
    input_text = input_text.replace("\"", "”")
    input_text = input_text.replace('\n', ' ')
    input_text = input_text.replace('\t', ' ')
    input_text = input_text.replace('\r', ' ')
    sentences = re.split('(?<=[.!,?”"]) +', input_text)

    processed_sentence_chunks = []
    for sentence in sentences:
        processed_sentence_chunks.append(process_sentence(sentence))

    consolidated_chunks = []

    for chunks in processed_sentence_chunks:
        for chunk in chunks:
            # print("consolidating", chunk)
            consolidated_chunks.append(consolidate_chunk(chunk))
    return consolidate_document(consolidated_chunks)


def process_sentence(sentence):
    doc = nlp(sentence)
    if non_punct_count(doc) <= NO_SPLIT_LIMIT:
        return [[token for token in doc]]

    all_phrases = []
    current_phrase = []
    for token in doc:
        # print(token.text, token.dep_, token.pos_, token.lemma_)
        if token.pos_ in [ADP, AUX, CONJ, SCONJ, CCONJ] or token.dep_ in [advcl, ROOT, prep, advmod]:
            # or (token.pos_ == PUNCT and token.text in [","])) and token.dep_ != neg:
            if non_punct_count(current_phrase) > MIN_PHRASE_LENGTH:
                all_phrases.append(current_phrase)
                current_phrase = []
        current_phrase.append(token)

    if len(current_phrase) > 0:
        all_phrases.append(current_phrase)

    combine_phrases(all_phrases)
    return all_phrases


def combine_phrases(phrases):
    if len(phrases) < 2:
        return
    phrase_lengths = [non_punct_count(phrase) for phrase in phrases]

    i = 0
    while i < len(phrases):
        if phrase_lengths[i] < MAX_PHRASE_LENGTH:
            if i == 0:
                if phrase_lengths[i + 1] + phrase_lengths[i] <= MAX_PHRASE_LENGTH:
                    break
            elif i == len(phrases) - 1:
                if phrase_lengths[i - 1] + phrase_lengths[i] <= MAX_PHRASE_LENGTH:
                    break
            elif phrase_lengths[i - 1] + phrase_lengths[i] <= MAX_PHRASE_LENGTH \
                    or phrase_lengths[i + 1] + phrase_lengths[i] <= MAX_PHRASE_LENGTH:
                break
        i += 1

    if i == len(phrases):
        return phrases

    merge_index = -1
    if i == 0:
        merge_index = 1
    elif i == len(phrases) - 1:
        merge_index = i - 1
    else:
        merge_index = i - 1 if phrase_lengths[i - 1] < phrase_lengths[i + 1] else i + 1

    smaller_index = i if i < merge_index else merge_index
    larger_index = i if i > merge_index else merge_index

    phrases[smaller_index].extend(phrases[larger_index])
    phrases.pop(larger_index)
    return combine_phrases(phrases)


def non_punct_count(tokens):
    return len(list(filter(lambda x: x.pos_ != PUNCT, tokens)))


def consolidate_chunk(chunk):
    consolidated_chunk = " ".join(token.text for token in chunk)  # join normally
    consolidated_chunk = re.sub(' ([,.;\)“’])', lambda m: m.group(1), consolidated_chunk)  # stick to left
    consolidated_chunk = re.sub('([\(“]) ', lambda m: m.group(1), consolidated_chunk)  # stick to right
    consolidated_chunk = re.sub(" (['“-]) ", lambda m: m.group(1), consolidated_chunk)  # join both sides
    return consolidated_chunk


def consolidate_document(phrases):
    indexes = [0]
    output_text = ""
    for phrase in phrases:
        output_text += phrase + " "
        indexes.append(len(output_text))

    return indexes, output_text


if __name__ == '__main__':
    # run!
    # app.run()
    assert len(sys.argv) == 2, "Missing artile file in CLI args!"

    input_file = sys.argv[1]
    input_text = open(input_file, "r", encoding="utf-8").read()
    print(input_text)

    indexes, output_text = process_input(input_text)

    for i in range(len(indexes)):
        if i == len(indexes) - 1:
            print(output_text[indexes[i]:])
        else:
            print(output_text[indexes[i]: indexes[i + 1]])

    print(output_text)

    write_article_to_db(input_file, output_text, indexes)
