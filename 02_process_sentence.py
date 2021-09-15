import argparse
import pickle
import re
from typing import List, Tuple

import nltk
from tqdm import tqdm

nltk.download("averaged_perceptron_tagger")


def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--review-path",
        type=str,
        default="reviews.pickle",
        help="resulting from format_amazon.py",
    )
    parser.add_argument(
        "--sentence-path",
        type=str,
        default="sentences.pickle",
        help="path to save sentences",
    )
    return parser.parse_args()


def get_sentences(s: str) -> List[str]:
    s = re.sub("[:,?!\n]", ".", s)
    sentences = [sent.strip() for sent in s.split(".") if sent.strip() != ""]
    return sentences


def get_sentence_attr(
    s: str, subj_words: List[str], noun_taggers: List[str], adj_taggers: List[str]
) -> Tuple[int, int, int, int]:

    subj_num = 0
    noun_num = 0
    adj_num = 0
    words = s.lower().split()
    w_t_list = nltk.pos_tag(words)

    for (w, t) in w_t_list:
        if w in subj_words:
            subj_num += 1
        if t in noun_taggers:
            noun_num += 1
        if t in adj_taggers:
            adj_num += 1
    return len(words), subj_num, noun_num, adj_num


def process_sentence(review_path: str, sentence_path: str) -> None:

    subj_words = [
        "i",
        "me",
        "my",
        "mine",
        "myself",
        "we",
        "us",
        "our",
        "ours",
        "ourselves",
    ]
    noun_taggers = ["NN", "NNP", "NNPS", "NNS"]
    adj_taggers = ["JJ", "JJR", "JJS"]

    with open(review_path, "rb") as rf:
        reviews = pickle.load(rf)

    sentences = []
    for idx, review in enumerate(tqdm(reviews, ncols=100)):
        text = review["text"]
        exps = get_sentences(text)
        for exp in exps:
            word_n, subj_n, noun_n, adj_n = get_sentence_attr(
                exp,
                subj_words=subj_words,
                noun_taggers=noun_taggers,
                adj_taggers=adj_taggers,
            )
            sentence = {
                "review_idx": idx,
                "exp": exp,
                "word_num": word_n,
                "subj_num": subj_n,
                "noun_num": noun_n,
                "adj_num": adj_n,
            }
            sentences.append(sentence)

    with open(sentence_path, "wb") as wf:
        pickle.dump(sentences, wf)


def main() -> None:
    args = parser_args()
    process_sentence(review_path=args.review_path, sentence_path=args.sentence_path)


if __name__ == "__main__":
    main()
