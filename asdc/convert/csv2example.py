#!/usr/bin/env python3

import argparse
import csv
import unicodedata
from pathlib import Path
from typing import Dict, Optional

from asdc.schema.example import Example, SimpleUtterance
from asdc.schema.id import SID, DocID
from asdc.schema.vanilla import VanillaUtterances


def item2scuds(text: str):
    text = text.replace("\n", "")
    if len(text) == 0:
        return []

    tmp = [v.strip() for v in unicodedata.normalize("NFKC", text).strip().split("。")]
    ret = []
    for v in tmp:
        if len(v) == 0:
            continue
        ret.append(f"{v}。")
    return ret


def operation(path_in: Path, path_out: Path, path_ref: Path) -> None:
    docid2vus: Optional[Dict[DocID, VanillaUtterances]] = None
    docid2vus = {}
    for f in path_ref.iterdir():
        with f.open() as inf:
            for line in inf:
                vus = VanillaUtterances.parse_raw(line)
                if vus.docid in docid2vus:
                    raise KeyError(f"Duplicated ID: {vus.docid}")
                docid2vus[vus.docid] = vus

    with path_in.open() as inf, path_out.open("w") as outf:
        r = csv.reader(inf)
        header = next(r)

        kvs = {}
        uttrid2sents = {}
        uttrid2found = set()

        idx_sid: int = header.index("ID")
        idx_sent: int = header.index("客発話")
        idx_scuds: int = header.index("解釈文")
        idx_memo: int = header.index("メモ")

        for items in r:
            scuds = item2scuds(items[idx_scuds])
            memo = unicodedata.normalize("NFKC", items[idx_memo]).strip()
            kvs[items[idx_sid]] = {
                "scuds": scuds,
                "memo": memo,
                "found": False,
            }
            sid = SID(id=items[idx_sid])

            if sid.uttrid.id not in uttrid2sents:
                uttrid2sents[sid.uttrid.id] = []
            uttrid2sents[sid.uttrid.id].append(items[idx_sent])
            if len(scuds) > 0:
                uttrid2found.add(sid.uttrid.id)

        for k, v in kvs.items():
            sid = SID(id=k)
            if sid.uttrid.id not in uttrid2found:
                continue

            scuds = v["scuds"]
            memo = v["memo"]

            ctx = []
            vus = docid2vus[sid.docid]
            for vu in vus.utterances[: sid.uttrid.num]:
                assert vu.name == "user" or vu.name == "agent"
                ctx.append(SimpleUtterance(name=vu.name, text=vu.text))
            ex = Example(
                sid=sid,
                sources=uttrid2sents[sid.uttrid.id],
                targets=scuds,
                context=ctx,
                purpose=vus.purpose,
                meta={},
            )
            if len(memo) > 0:
                ex.meta["memo"] = memo

            outf.write(ex.json(ensure_ascii=False, sort_keys=True))
            outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--ref", "-r", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.output, opts.ref)


if __name__ == "__main__":
    main()
