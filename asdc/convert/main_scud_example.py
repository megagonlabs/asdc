#!/usr/bin/env python3
import argparse
import collections
import json
from pathlib import Path
from typing import DefaultDict, Iterator, Literal

from asdc.schema.dialog import Docid2Utterances, Scud, Utterances, open_scud_file_by_docid
from asdc.schema.example import Example, VanillaUtterance
from asdc.schema.id import SID, DocID

METACHAR_LINE_BREAK: str = "\u2581"


def _get_purpose(orig: str) -> Literal["test", "train", "dev"]:
    if orig == "test":
        return orig
    elif orig == "dev":
        return orig
    elif orig != "train":
        raise NotImplementedError
    return "train"


def scuds2examples(docid: DocID, scuds: list[Scud], uttrs: Utterances) -> Iterator[Example]:
    sid2scuds: DefaultDict[SID, list[Scud]] = collections.defaultdict(list)
    for scud in scuds:
        sid2scuds[scud.sid].append(scud)

    for uttr in uttrs.utterances:
        if uttr.name.startswith("operator_"):
            continue

        for idx, _ in enumerate(uttr.yield_sentence()):
            context: list[VanillaUtterance] = uttrs.get_contexts(sid=uttr.id.get_sid(0), same_uttr=False, by_uttr=True)
            sid = uttr.id.get_sid(idx)
            sources: list[str] = [s for s in uttrs.utterances[sid.uttrid.num].yield_sentence()]

            my_scuds = sid2scuds.get(sid)
            if my_scuds is None:
                # nothing output
                yield Example(
                    sid=sid,
                    sources=sources,
                    targets=[],
                    context=context,
                    purpose=_get_purpose(uttrs.meta.purpose),
                    meta={},
                    correct=True,
                    example_types=None,
                    original_sid=None,
                )
                continue

            gts = set()
            uttr_ids = set()
            internal_sids: set[SID] = set()
            for scud in sid2scuds[sid]:
                for sg in scud.groups:
                    gts.add(str(sg.group_type))
                    for _span in sg.spans:
                        uttr_ids.add(_span.sid.uttrid)
                        if len(sg.spans) > 1 and _span.sid.uttrid == sid.uttrid:
                            internal_sids.add(_span.sid)

            assert len(uttr_ids) > 0

            if len(internal_sids) > 0:
                internal_sids.add(sid)

            yield Example(
                sid=sid,
                sources=sources,
                targets=[s.scud for s in sorted(my_scuds)],
                context=context,
                purpose=_get_purpose(uttrs.meta.purpose),
                meta={},
                correct=True,
                example_types=None,
                original_sid=None,
            )


def generate(path_in: Path, ref: Path) -> Iterator[Example]:
    d2u = Docid2Utterances(ref)
    docid2scuds = open_scud_file_by_docid(path_in)
    for docid, scuds in sorted(docid2scuds.items()):
        uttrs = d2u[docid]
        for e in scuds2examples(docid, scuds, uttrs):
            e.meta["source"] = "main"
            yield e


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--ref", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    with opts.output.open("w") as outf:
        for e in generate(opts.input, opts.ref):
            v = json.dumps(e.model_dump(), ensure_ascii=False, sort_keys=True)
            outf.write(f"{v}\n")


if __name__ == "__main__":
    main()
