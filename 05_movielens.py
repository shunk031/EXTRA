import argparse
import json
import pathlib
import pickle
from datetime import datetime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--id-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent / "outputs" / "ids.pickle",
        help="resulting from `keep_valid.py`",
    )
    parser.add_argument(
        "--id2exp-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent / "outputs" / "id2exp.json",
        help="resulting from `keep_valid.py`",
    )
    parser.add_argument(
        "--id-txt-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent / "outputs" / "ids.txt",
        help="path to save explanation IDs in plain text",
    )
    parser.add_argument(
        "--id2exp-txt-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent / "outputs" / "id2exp.txt",
        help="path to save id2exp in plain text",
    )

    return parser.parse_args()


def movielens(
    id_path: pathlib.Path,
    id_txt_path: pathlib.Path,
    id2exp_path: pathlib.Path,
    id2exp_txt_path: pathlib.Path,
) -> None:

    with open(id_path, "rb") as rf:
        IDs = pickle.load(rf)

    lines = []
    for record in IDs:
        # userID::itemID::rating::timestamp::expID:expID::oexpID:oexpID
        user = record["user"]
        item = record["item"]
        rating = record["rating"]
        time = int(datetime.strptime(record["time"], "%Y-%m-%d").timestamp())
        exp_idx = record["exp_idx"]
        oexp_idx = record["oexp_idx"]
        exp = ":".join(exp_idx)
        oexp = ":".join(oexp_idx)
        line = "::".join([user, item, str(rating), str(time), exp, oexp])
        lines.append(line)

    with open(id_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    with open(id2exp_path, "r", encoding="utf-8") as f:
        id2exp = json.load(f)
    lines = []
    for (idx, exp) in id2exp.items():
        # expID::exp
        line = "::".join([idx, exp])
        lines.append(line)
    with open(id2exp_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    args = parse_args()
    movielens(
        id_path=args.id_path,
        id_txt_path=args.id_txt_path,
        id2exp_path=args.id2exp_path,
        id2exp_txt_path=args.id2exp_txt_path,
    )


if __name__ == "__main__":
    main()
