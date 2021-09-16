import argparse
import json
import pathlib
import re
from multiprocessing import Pool
from typing import List, Tuple

import nltk
from tqdm import tqdm

nltk.download("averaged_perceptron_tagger")


def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--review-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve() / "outputs" / "reviews.jsonl",
        help="resulting from format_amazon.py",
    )
    parser.add_argument(
        "--sentence-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve() / "outputs" / "sentences.jsonl",
        help="path to save sentences",
    )
    parser.add_argument("--n-processes", type=int, default=8)
    return parser.parse_args()


def get_sentences(s: str) -> List[str]:
    s = re.sub("[:,?!\n]", ".", s)
    sentences = [sent.strip() for sent in s.split(".") if sent.strip() != ""]
    return sentences


def get_sentence_attr(s: str) -> Tuple[int, int, int, int]:

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


def process_sentence_mp(idx_review):

    idx, review = idx_review
    text = review["text"]
    exps = get_sentences(text)

    sentences = []

    for exp in exps:
        word_n, subj_n, noun_n, adj_n = get_sentence_attr(exp)

        sentence = {
            "review_idx": idx,
            "exp": exp,
            "word_num": word_n,
            "subj_num": subj_n,
            "noun_num": noun_n,
            "adj_num": adj_n,
        }

        sentences.append(sentence)
    return sentences


def process_sentence(
    review_path: str, sentence_path: str, n_processes: int = 8
) -> None:

    with open(review_path, "r") as rf:
        reviews = [json.loads(line) for line in tqdm(rf)]

    all_sentences = []
    with Pool(processes=n_processes) as p:
        with tqdm(total=len(reviews), ncols=100) as pbar:
            iterator = p.imap(process_sentence_mp, enumerate(reviews))
            for sentences in tqdm(iterator, ncols=100):
                all_sentences.extend(sentences)
                pbar.update()

    with open(sentence_path, "w") as wf:
        for sentence in tqdm(all_sentences, ncols=100, desc="Save to jsonl"):
            json.dump(sentence, wf)
            wf.write("\n")


def main() -> None:
    args = parser_args()

    process_sentence(
        review_path=args.review_path,
        sentence_path=args.sentence_path,
        n_processes=args.n_processes,
    )


if __name__ == "__main__":
    main()
