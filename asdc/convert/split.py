#!/usr/bin/env python3

import argparse
from pathlib import Path

from asdc.schema.example import Example


def operation(
    path_in: Path,
    path_train: Path,
    path_dev: Path,
    path_test: Path,
    size_context: int,
    train_max_distance_uttr: int,
    test_max_distance_uttr: int,
) -> None:
    assert size_context >= 0
    assert train_max_distance_uttr >= 0
    assert test_max_distance_uttr >= 0

    with path_train.open("w") as outf_train, path_dev.open("w") as outf_dev, path_test.open(
        "w"
    ) as outf_test, path_in.open() as inf:
        for line in inf:
            ex = Example.parse_raw(line)
            purpose = ex.meta["purpose"]
            outline: str = ex.json(ensure_ascii=False, sort_keys=True) + "\n"

            if purpose == "train":
                if ex.max_distance_uttr > train_max_distance_uttr:
                    continue
                outf_train.write(outline)

            elif purpose == "dev":
                if ex.max_distance_uttr > train_max_distance_uttr:
                    continue
                outf_dev.write(outline)

            elif purpose == "test":
                if ex.max_distance_uttr > test_max_distance_uttr:
                    continue
                outf_test.write(outline)

            else:
                raise NotImplementedError(purpose)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--train", type=Path, required=True)
    oparser.add_argument("--dev", type=Path, required=True)
    oparser.add_argument("--test", type=Path, required=True)

    oparser.add_argument("--context", type=int, default=0)
    oparser.add_argument("--train_max_distance_uttr", type=int, default=0)
    oparser.add_argument("--test_max_distance_uttr", type=int, default=9999)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        opts.input,
        opts.train,
        opts.dev,
        opts.test,
        opts.context,
        opts.train_max_distance_uttr,
        opts.test_max_distance_uttr,
    )


if __name__ == "__main__":
    main()
