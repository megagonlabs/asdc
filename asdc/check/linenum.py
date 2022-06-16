#!/usr/bin/env python3

import argparse
from pathlib import Path


def operation(path_in: Path, path_root: Path) -> None:
    to_be_checked = []
    with path_in.open() as inf:
        for line in inf:
            if ".VanillaUtterances.jsonl``" in line:
                if ":" not in line:
                    continue

                fname = line.split("``")[1].split("``")[0]

                num = int(line.split(":")[1].split()[0].replace(",", ""))
                to_be_checked.append((fname, num))

    fnames = set([v[0] for v in to_be_checked])

    if len(fnames) != len([v for v in path_root.glob("*.jsonl")]):
        raise KeyError("Insufficient number of file names: {fnames} {")

    fname2linenum = {}
    for fname in fnames:
        with path_root.joinpath(fname).open() as inf:
            fname2linenum[fname] = len(inf.readlines())

    for fname, num in to_be_checked:
        gold = fname2linenum[fname]
        if gold != num:
            raise KeyError(f"{fname}: The number of lines is not {num} but {gold}")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--root", "-r", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.root)


if __name__ == "__main__":
    main()
