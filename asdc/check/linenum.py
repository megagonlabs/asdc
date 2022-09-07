#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List


def check_end(tail_list: List[str], line: str) -> bool:
    for tail in tail_list:
        if line.strip().endswith(tail):
            return True
    return False


def operation(path_in: Path, path_root: Path, suffix: str, tail_list: List[str]) -> None:
    to_be_checked = []
    with path_in.open() as inf:
        for line in inf:
            if suffix in line and check_end(tail_list, line):
                fname = line.split("``")[1].split("``")[0]

                num = int(line.split(":")[1].split()[0].replace(",", ""))
                to_be_checked.append((fname, num))

    fnames = set([v[0] for v in to_be_checked])
    target_files = set([v.name for v in path_root.glob("*.jsonl")])

    if len(fnames ^ target_files) > 0:
        raise KeyError(f"Insufficient number of file names: { fnames ^ target_files}")

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
    oparser.add_argument("--suffix", "-s", required=True)
    oparser.add_argument("--tail", action="append")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.root, opts.suffix, opts.tail)


if __name__ == "__main__":
    main()
