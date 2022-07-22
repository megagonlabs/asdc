#!/usr/bin/env python3

import argparse
import collections
from pathlib import Path
from typing import DefaultDict, Iterator, List, Optional, Set

from asdc.schema.dialog import Docid2Utterances, Scud, Utterances, open_scud_file_by_docid
from asdc.schema.example import Alignment, AlignmentSpan, Example, SimpleUtterance
from asdc.schema.id import SID, DocID

METACHAR_LINE_BREAK: str = "\u2581"


def scuds2examples(docid: DocID, scuds: List[Scud], uttrs: Utterances) -> Iterator[Example]:
    sid2scuds: DefaultDict[SID, List[Scud]] = collections.defaultdict(list)
    for scud in scuds:
        sid2scuds[scud.sid].append(scud)

    for uttr in uttrs.utterances:
        if uttr.name.startswith("operator_"):
            continue

        for idx, _ in enumerate(uttr.yield_sentence()):
            context: List[SimpleUtterance] = uttrs.get_contexts(sid=uttr.id.get_sid(0), same_uttr=False, by_uttr=True)
            sid = uttr.id.get_sid(idx)
            sources: List[str] = [s for s in uttrs.utterances[sid.uttrid.num].yield_sentence()]

            my_scuds = sid2scuds.get(sid)
            if my_scuds is None:
                # nothing output
                yield Example(
                    sid=sid,
                    sources=sources,
                    source_index=sid.sentence_num,
                    targets=[],
                    group_types=[],
                    max_distance_uttr=0,
                    max_distance_sentence=0,
                    context=context,
                    meta={"purpose": uttrs.meta.purpose},
                    alignments_list=[],
                )
                continue

            gts = set()
            uttr_ids = set()
            internal_sids: Set[SID] = set()
            for scud in sid2scuds[sid]:
                for sg in scud.groups:
                    gts.add(str(sg.group_type))
                    for _span in sg.spans:
                        uttr_ids.add(_span.sid.uttrid)
                        if len(sg.spans) > 1 and _span.sid.uttrid == sid.uttrid:
                            internal_sids.add(_span.sid)

            assert len(uttr_ids) > 0
            max_distance_uttr: int = max(uttr_ids) - min(uttr_ids)

            max_distance_sentence: Optional[int] = None
            if len(internal_sids) > 0:
                internal_sids.add(sid)
                max_distance_sentence = max(internal_sids) - min(internal_sids)  # type: ignore Temporary fix

            yield Example(
                sid=sid,
                sources=sources,
                source_index=sid.sentence_num,
                targets=[s.scud for s in sorted(my_scuds)],
                group_types=sorted(list(gts)),
                max_distance_uttr=max_distance_uttr,
                max_distance_sentence=max_distance_sentence,
                context=context,
                meta={"purpose": uttrs.meta.purpose},
                alignments_list=_get_alighment(
                    context,
                    sources,
                    my_scuds,
                    uttrs,
                ),
            )


def _get_alighment(
    context: List[SimpleUtterance], sources: List[str], scuds: List[Scud], uttrs: Utterances
) -> List[List[Alignment]]:
    def _context_new_position(sid: SID, position: int) -> int:
        np: int = 0
        for idx, sent in enumerate(uttrs.utterances[sid.uttrid.num].yield_sentence()):
            if idx == sid.sentence_num:
                break
            np += len(sent)
        return np + position

    alignments_list: List[List[Alignment]] = []
    for scud in scuds:
        alignments: List[Alignment] = []
        for group in scud.groups:
            if not group.has_target or not group.has_source:
                continue

            _al_origins: List[AlignmentSpan] = []
            _al_origins_in_context: List[bool] = []
            _al_targets: List[AlignmentSpan] = []

            for span in group.spans:
                if span.is_target:
                    _al_targets.append(AlignmentSpan(index=scud.idx, start=span.start, end=span.end))
                else:
                    if span.sid.uttrid == scud.sid.uttrid:
                        _al_origins.append(
                            AlignmentSpan(
                                index=span.sid.sentence_num,
                                start=span.start,
                                end=span.end,
                            )
                        )
                        _al_origins_in_context.append(False)
                    else:
                        _al_origins.append(
                            AlignmentSpan(
                                index=span.sid.uttrid.num,
                                start=_context_new_position(span.sid, span.start),
                                end=_context_new_position(span.sid, span.end),
                            )
                        )
                        _al_origins_in_context.append(True)

            alignments.append(
                Alignment(
                    origins=_al_origins,
                    origins_in_context=_al_origins_in_context,
                    targets=_al_targets,
                )
            )
        alignments_list.append(sorted(alignments, key=lambda x: min(x.targets)))
    return alignments_list


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
            outf.write(f"{e.json(ensure_ascii=False, sort_keys=True)}\n")


if __name__ == "__main__":
    main()
