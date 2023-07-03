#!/usr/bin/env python3

import argparse
from pathlib import Path

from asdc.schema.example import Example, VanillaUtterances
from asdc.schema.id import SID, DocID


def operation(path_vuttr_list: list[Path], path_ex_list: list[Path]) -> None:
    docids: set[DocID] = set()
    sids: set[SID] = set()

    count_vuttrs: int = 0
    count_vuttr: int = 0
    for _path_vuttr in path_vuttr_list:
        for path_vuttr in _path_vuttr.iterdir():
            with path_vuttr.open() as inf:
                for line in inf:
                    vuttr = VanillaUtterances.model_validate_json(line)
                    if vuttr.docid in docids:
                        raise KeyError(f"Duplicated DocID: {vuttr.docid} ({path_vuttr})")
                    count_vuttrs += 1
                    count_vuttr += len(vuttr.utterances)
                    docids.add(vuttr.docid)
                    sids.add(SID(id=vuttr.docid.id + "-0"))
    print(f"# VanillaUtterances: {count_vuttrs:,}")
    print(f"# VanillaUtterance: {count_vuttr:,}")

    count_ex: int = 0
    for _path_ex in path_ex_list:
        for path_ex in _path_ex.iterdir():
            with path_ex.open() as inf:
                for line in inf:
                    ex = Example.model_validate_json(line)
                    if ex.sid in sids:
                        raise KeyError(f"Duplicated SID: {ex.sid} ({path_ex})")
                    sids.add(ex.sid)
                    count_ex += 1
    print(f"# Example: {count_ex:,}")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--vuttr", type=Path, action="append")
    oparser.add_argument("--ex", type=Path, action="append")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.vuttr, opts.ex)


if __name__ == "__main__":
    main()
