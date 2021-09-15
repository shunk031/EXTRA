import argparse
import gzip
import json
from datetime import datetime

from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--raw-path",
        type=str,
        default="reviews_Movies_and_TV_5.json.gz",
        help="path to load raw reviews",
    )
    parser.add_argument(
        "--review-path", type=str, default="reviews.jsonl", help="path to save reviews"
    )
    return parser.parse_args()


def format_amazon(raw_path: str, review_path: str) -> None:

    lines = []
    with gzip.open(raw_path, "r") as rf:
        for line in rf:
            lines.append(line)

    reviews = []
    for line in tqdm(lines, ncols=100):
        review = eval(line)

        text = ""
        if "summary" in review:
            summary = review["summary"]
            if summary != "":
                text += summary + "\n"
        text += review["reviewText"]

        json_doc = {
            "user": review["reviewerID"],
            "item": review["asin"],
            "rating": int(review["overall"]),
            "text": text,
            "time": datetime.fromtimestamp(int(review["unixReviewTime"])).strftime(
                "%Y-%m-%d"
            ),
        }
        reviews.append(json_doc)

    with open(review_path, "w") as wf:
        for review in reviews:
            json.dump(review, wf)
            wf.write("\n")


def main() -> None:
    args = parse_args()
    format_amazon(raw_path=args.raw_path, review_path=args.review_path)


if __name__ == "__main__":
    main()
