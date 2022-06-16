#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Set

from asdc.schema.example import Example
from asdc.schema.id import SID, DocID
from asdc.schema.vanilla import VanillaUtterances


def operation(path_vuttr_list: List[Path], path_ex_list: List[Path]) -> None:
    docids: Set[DocID] = set()
    sids: Set[SID] = set()

    for _path_vuttr in path_vuttr_list:
        for path_vuttr in _path_vuttr.iterdir():
            with path_vuttr.open() as inf:
                for line in inf:
                    vuttr = VanillaUtterances.parse_raw(line)
                    if vuttr.meta.id in docids:
                        raise KeyError(f"Duplicated DocID: {vuttr.meta.id} ({path_vuttr})")
                    docids.add(vuttr.meta.id)
                    sids.add(SID(id=vuttr.meta.id.id + "-0"))

    for _path_ex in path_ex_list:
        for path_ex in _path_ex.iterdir():
            with path_ex.open() as inf:
                for line in inf:
                    ex = Example.parse_raw(line)
                    if ex.sid in sids:
                        raise KeyError(f"Duplicated SID: {ex.sid} ({path_ex})")
                    sids.add(ex.sid)


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
