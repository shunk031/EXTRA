import argparse
import json
import pathlib
import pickle
from multiprocessing import Pool

from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--review-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.resolve() / "outputs" / "reviews.jsonl",
        help="resulting from `format_amazon.py`",
    )
    parser.add_argument(
        "--sentence-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.resolve()
        / "outputs"
        / "sentences.pickle",
        help="resulting from `process_sentence.py`",
    )
    parser.add_argument(
        "--group-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.resolve()
        / "outputs"
        / "groups0.9.pickle",
        help="resulting from `group_sentence.py`",
    )
    parser.add_argument(
        "--id-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.resolve() / "outputs" / "ids.jsonl",
        help="path to save explanation IDs",
    )
    parser.add_argument(
        "--id2exp-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent.resolve() / "outputs" / "id2exp.json",
        help="path to save id2exp",
    )
    parser.add_argument("--n-processes", type=int, default=8)
    return parser.parse_args()


def keep_valid(
    review_path: pathlib.Path,
    sentence_path: pathlib.Path,
    group_path: pathlib.Path,
    id_path: pathlib.Path,
    id2exp_path: pathlib.Path,
    n_processes: int = 8,
) -> None:

    with open(review_path, "r") as rf:
        reviews = [
            json.loads(line) for line in tqdm(rf, desc=f"Load {review_path.name}")
        ]

    with open(sentence_path, "r") as rf:
        raw_sentences = [line for line in tqdm(rf, desc=f"Load {sentence_path.name}")]

    sentences = []
    with Pool(processes=n_processes) as p:
        with tqdm(total=len(raw_sentences), ncols=100) as pbar:
            for sentence in tqdm(p.imap(json.loads, raw_sentences), ncols=100):
                sentences.append(sentence)
                pbar.update()

    with open(group_path, "rb") as rf:
        exp_id_groups = pickle.load(rf)

    id2doc = {}
    for group in exp_id_groups:
        exp_idx = list(group)[0]  # keep one explanation in each group
        for oexp_idx in group:
            sentence = sentences[oexp_idx]
            review_idx = sentence["review_idx"]
            if review_idx not in id2doc:
                review = reviews[review_idx]
                json_doc = {
                    "user": review["user"],
                    "item": review["item"],
                    "rating": review["rating"],
                    "time": review["time"],
                    "exp_idx": [str(exp_idx)],
                    "oexp_idx": [str(oexp_idx)],
                }
                id2doc[review_idx] = json_doc
            else:
                id2doc[review_idx]["exp_idx"].append(str(exp_idx))
                id2doc[review_idx]["oexp_idx"].append(str(oexp_idx))

    IDs = []
    idx_set = set()
    for _, doc in id2doc.items():
        IDs.append(doc)
        exp_idx = doc["exp_idx"]
        oexp_idx = doc["oexp_idx"]
        idx_set |= set(exp_idx) | set(oexp_idx)

    with open(id_path, "wb") as wf:
        pickle.dump(IDs, wf)

    id2exp = {}
    for idx, sentence in enumerate(sentences):
        s_idx = str(idx)
        if s_idx in idx_set:
            id2exp[s_idx] = sentence["exp"]

    with open(id2exp_path, "w", encoding="utf-8") as f:
        json.dump(id2exp, f, indent=4)


def main() -> None:

    args = parse_args()
    keep_valid(
        review_path=args.review_path,
        sentence_path=args.sentence_path,
        group_path=args.group_path,
        id_path=args.id_path,
        id2exp_path=args.id2exp_path,
        n_processes=args.n_processes,
    )


if __name__ == "__main__":
    main()
