import argparse
import datetime
import json
import os
import pathlib
import pickle
from functools import partial
from multiprocessing import Pool
from typing import List

from datasketch import LeanMinHash, MinHash, MinHashLSH
from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sentence-path",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent / "outputs" / "sentences.jsonl",
        help="resulting from `02_process_sentence.py`",
    )
    parser.add_argument(
        "--directory",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent / "outputs",
        help="directory to save the grouped sentence ids",
    )
    parser.add_argument(
        "--sim-thresholds",
        nargs="+",
        type=float,
        default=(0.9,),
        help="the similarity between two near duplicates. To test more in this way [0.9, 0.85, 0.7]",
    )
    parser.add_argument(
        "--shingle-size",
        type=int,
        default=2,
        help="preseve the word order to some extent",
    )
    parser.add_argument(
        "--group-size",
        type=int,
        default=5,
        help="minimum number of sentences in a group",
    )
    parser.add_argument("--n-processes", type=int, default=os.cpu_count())

    return parser.parse_args()


def now_time():
    """a string of current time"""
    return "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") + "]: "


def get_k_shingles(raw_text, k=1):
    text_lower = raw_text.lower()
    words = text_lower.split()
    if k == 1:
        return set(words)

    shingles = []
    for start in range(len(words) + 1 - k):
        k_words = words[start : (start + k)]
        k_shingle = " ".join(k_words)
        shingles.append(k_shingle)
    return set(shingles)


def is_target_sentence(sentence, shingle_size: int) -> bool:

    if sentence["word_num"] < shingle_size:
        return False
    if sentence["subj_num"] > 0:
        return False
    if sentence["noun_num"] < 1:
        return False
    if sentence["adj_num"] < 1:
        return False

    return True


def minhash_mp(sentence, shingle_size: int):
    exp = sentence["exp"]
    shingle_set = get_k_shingles(exp, shingle_size)
    mh = MinHash()  # create MinHash for exp
    for s in shingle_set:
        mh.update(s.encode("utf8"))  # convert shingle s into MinHash

    return LeanMinHash(mh)


def group_sentence(
    sentence_path: str,
    shingle_size: int,
    sim_thresholds: List[int],
    group_size: int,
    directory: str,
    n_processes: int,
):

    print(now_time() + "Program running")

    with open(sentence_path, "rb") as rf:
        sentences = pickle.load(rf)

    # with open(sentence_path, 'r') as rf:
    #     sentences = [json.loads(line) for line in tqdm(rf)]

    sentences = list(
        filter(
            lambda x: is_target_sentence(x, shingle_size=shingle_size),
            tqdm(sentences, ncols=100, desc="Filter sentences"),
        )
    )

    minhash_dict = {}  # all sentences' MinHash
    with Pool(processes=n_processes) as p:
        with tqdm(total=len(sentences), ncols=100) as pbar:
            partial_minhash_mp = partial(minhash_mp, shingle_size=shingle_size)
            mp_iterator = p.imap(partial_minhash_mp, sentences)

            for idx, lean_min_hash in enumerate(tqdm(mp_iterator, ncols=100)):
                minhash_dict[idx] = lean_min_hash
                pbar.update()

    print(now_time() + "Created Minhash")
    del sentences  # to save memory

    # create MinHash for once, when testing multiple similarity values
    for sim_threshold in sim_thresholds:
        lsh = MinHashLSH(threshold=sim_threshold)  # create LSH index
        for idx, mh in minhash_dict.items():
            lsh.insert(str(idx), mh)
        print(now_time() + "Created LSH for similarity {}".format(sim_threshold))

        queried_ids = set()  # way more efficient than list
        exp_id_groups = []
        for idx, mh in minhash_dict.items():
            if idx in queried_ids:
                continue

            # id list of one group of duplicate sentences
            one_group_ids_str = lsh.query(mh)

            for i in one_group_ids_str:
                lsh.remove(i)  # for efficiency
            one_group_ids_int = [int(i) for i in one_group_ids_str]
            if len(one_group_ids_int) > group_size:
                # only keep a group with enough sentences
                exp_id_groups.append(one_group_ids_int)

            for i in one_group_ids_int:
                queried_ids.add(i)

        with open(directory + "groups{}.pickle".format(sim_threshold), "wb") as wf:
            pickle.dump(exp_id_groups, wf)

        print(now_time() + "Saved a file for similarity {}".format(sim_threshold))


def main():
    args = parse_args()

    group_sentence(
        sentence_path=args.sentence_path,
        shingle_size=args.shingle_size,
        sim_thresholds=args.sim_thresholds,
        group_size=args.group_size,
        directory=args.directory,
        n_processes=args.n_processes,
    )


if __name__ == "__main__":
    main()
