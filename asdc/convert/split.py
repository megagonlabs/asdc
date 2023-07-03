#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from asdc.schema.example import Example


def operation(
    path_in: Path,
    path_train: Path,
    path_dev: Path,
    path_test: Path,
) -> None:
    with path_train.open("w") as outf_train, path_dev.open("w") as outf_dev, path_test.open(
        "w"
    ) as outf_test, path_in.open() as inf:
        for line in inf:
            ex = Example.model_validate_json(line)
            purpose = ex.purpose
            outline: str = json.dumps(ex.model_dump(), ensure_ascii=False, sort_keys=True) + "\n"

            if purpose == "train":
                outf_train.write(outline)
            elif purpose == "dev":
                outf_dev.write(outline)
            elif purpose == "test":
                outf_test.write(outline)
            else:
                raise NotImplementedError(purpose)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--train", type=Path, required=True)
    oparser.add_argument("--dev", type=Path, required=True)
    oparser.add_argument("--test", type=Path, required=True)

    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        opts.input,
        opts.train,
        opts.dev,
        opts.test,
    )


if __name__ == "__main__":
    main()
