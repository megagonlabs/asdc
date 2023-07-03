#!/usr/bin/env python3

import argparse
import collections
import csv
import json
import typing
import unicodedata
from pathlib import Path

from asdc.schema.dialog import Scud, Utterances
from asdc.schema.id import SID

ScudData = typing.NewType("ScudData", typing.DefaultDict[SID, typing.List[Scud]])


def parse(path_in: Path, scud: ScudData, path_out: Path):
    path_out.mkdir(exist_ok=True, parents=True)
    for fpath in sorted(path_in.iterdir()):
        with fpath.open() as fp:
            uttrs = Utterances.model_validate_json(fp.read())
        myid: str = uttrs.meta.id.doc_num_str

        with path_out.joinpath(f"{myid}.scud.jsonl").open("w") as outaf:
            for uttr in uttrs.utterances:
                for sidx, sent in enumerate(uttr.yield_sentence(meta=True)):
                    sid: SID = uttr.id.get_sid(sidx)
                    _scuds = scud.get(sid)

                    if _scuds is None:
                        continue

                    for _s in _scuds:
                        _s.text = sent
                        outaf.write(json.dumps(_s.model_dump(), ensure_ascii=False, sort_keys=True))
                        outaf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--scud", "-s", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    return oparser.parse_args()


def parse_scud(path_in: Path) -> ScudData:
    data: ScudData = ScudData(collections.defaultdict(list))

    with path_in.open() as inf:
        reader = csv.reader(inf)
        _ = next(reader)
        for row in reader:
            _myid = row[0].strip()
            if len(_myid) == 0:
                continue
            myid = SID(id=_myid)
            myscud = unicodedata.normalize("NFKC", row[1].strip())
            if len(myscud) == 0:
                continue
            scud = Scud(
                sid=myid,
                idx=len(data.get(myid, [])),
                text="",
                scud=myscud,
                queries=list(filter(None, row[2].split("\n"))),
                memo=unicodedata.normalize("NFKC", row[3]),
                groups=[],
            )

            data[myid].append(scud)
    return data


def main() -> None:
    opts = get_opts()
    scud = parse_scud(opts.scud)
    parse(opts.input, scud, opts.output)


if __name__ == "__main__":
    main()
