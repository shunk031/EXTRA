# EXTRA (EXplanaTion RAnking) Datasets

## Paper
> Lei Li, Yongfeng Zhang, Li Chen. EXTRA: Explanation Ranking Datasets for Explainable Recommendation. SIGIR'21 Resource. \[[Paper](https://arxiv.org/abs/2102.10315)\]

## Datasets to [download](https://drive.google.com/drive/folders/1Kb4pOCUja1EgDlhP-YQI8AxofHBkioT5?usp=sharing)
- Amazon Movies & TV
- TripAdvisor Hong Kong
- Yelp 2019

## Data format

- **IDs.pickle** can be loaded via the pickle package as a python list, where each record is a python dict in the form of

```json
{
	"user": "7B555091EC0818119062CF726B9EF5FF",  # str
	"item": "1068719",       # str
	"rating": 5,             # int, not important to the ranking task
	"time": "2017-05-06",    # str in the format of YYYY-MM-DD, not available on TripAdvisor
	"exp_idx": ["34", "85"], # a list of str, they are the indices of explanations after sentence grouping via LSH
	"oexp_idx": ["91", "15"] # a list of str, they are the indices of original sentences, corresponding to senID in the following
}  
```

- Open **id2exp.json** via a text editor, e.g., Sublime, if you are curious about what the explanation indices correspond to. Or you can load it via [testing.py](testing.py) by updating the parameters (line 5-7).

---
- **IDs.txt** and **id2exp.txt** are compatible with **IDs.pickle** and **id2exp.json**. It would be easier to check the content with plain text files.
- Each line in **IDs.txt** is in the format of ```userID::itemID::rating::timestamp::expID:expID::senID:senID```, where timestamp is not available on TripAdvisor, and expID/senID are separated by ":" when there are multiple explanations.
- Each line in **id2exp.txt** is in the format of ```expID::explanation sentence```.
- You can load the two files via [movielens_load.py](movielens_load.py) by updating the paths (line 1-2).
---
- **Folders** named 1, 2, 3, 4 and 5 are data splits.
- Each folder contains **train.index** and **test.index** which indicate the indices of their records in the list of IDs.pickle/IDs.txt.
- **train.index**/**test.index** contain a line of numbers (indices), e.g., 5 8 9 10.

## Creation steps

- Run the scripts in the following order:

```shell
python 01_format_amazon.py \
	--raw-path SIGIR21-EXTRA-Datasets/reviews_Movies_and_TV_5.json.gz \
	--review-path outputs/reviews.jsonl
```

```shell
python 02_process_sentence.py \
	--review-path outputs/reviews.jsonl \
	--sentence-path sentences.jsonl --n-processes 8
```

```shell
python 03_group_sentence.py \
	--sentence-path outputs/sentences.jsonl \
	--directory outputs/ \
	--sim-thresholds 0.9 \
	--shingle-size 2 \
	--group-size 5 \
	--n-processes 8
```

- Update the paths (line 5-9) in [keep_valid.py](keep_valid.py).
- Update the paths (line 6-9) in [movielens.py](movielens.py), if you want to process the data into the MovieLens format.

## Friendly reminder
- Run the program on a machine with sufficient memory
- Creating the datasets may take some time (e.g., hours for Yelp)

## Code dependency
- Python 3.6
- NLTK
- [Datasketch](http://ekzhu.com/datasketch/lsh.html)

## Citation
```
@inproceedings{SIGIR21-EXTRA,
	title={EXTRA: Explanation Ranking Datasets for Explainable Recommendation},
	author={Li, Lei and Zhang, Yongfeng and Chen, Li},
	booktitle={SIGIR},
	year={2021}
}
```
