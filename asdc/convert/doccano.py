#!/usr/bin/env python3

import argparse
import difflib
import json
import sys
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterator, List, NewType, Optional, Tuple, Union

from pydantic import BaseModel

from asdc.check.format import check_scud_groups
from asdc.schema.dialog import Docid2Utterances, GroupType, Scud, Sid2Scuds, Span, SpanGroup, Utterances, open_scud_file
from asdc.schema.id import SID

SEPARATOR: str = "\r\n"

PREFIX_OUTSIDE: str = "外"
PREFIX_BOTHSIDE: str = "両"


def label2group_type(label: str) -> GroupType:
    if label == "エラー":
        return GroupType.ERROR
    elif label.startswith(PREFIX_OUTSIDE):
        return GroupType.OUTSIDE
    elif label.startswith(PREFIX_BOTHSIDE):
        return GroupType.BOTHSIDE
    return GroupType.INSIDE


class DoccanoAnnotation(BaseModel):
    id: str
    text: str
    meta: Dict[str, Any]
    labels: List[List[Union[int, str]]]
    annotation_approver: Optional[str]

    def get_sid(self) -> SID:
        return Scud.id2sid(self.text.split(SEPARATOR)[-3])

    def get_idx(self) -> int:
        return Scud.id2idx(self.text.split(SEPARATOR)[-3])

    def get_sentence(self) -> str:
        return self.text.split(SEPARATOR)[-2]

    def get_scud_text(self) -> str:
        return self.text.split(SEPARATOR)[-1]

    def get_offset_sid(self) -> int:
        items = self.text.split(SEPARATOR)
        return len(SEPARATOR.join([v for v in items[:-3]])) + len(SEPARATOR) * 2

    def get_offset_sentence(self) -> int:
        items = self.text.split(SEPARATOR)
        return len(SEPARATOR.join([v for v in items[:-2]])) + len(SEPARATOR)

    def get_offset_scud(self) -> int:
        items = self.text.split(SEPARATOR)
        return len(SEPARATOR.join([v for v in items[:-1]])) + len(SEPARATOR)

    def get_sid_and_offset(self, original_idx: int, uttrs: Utterances) -> Tuple[SID, int]:
        cnt = 0
        for _us in uttrs.utterances:
            for sidx, sent in enumerate(_us.yield_sentence(meta=True)):
                new_cnt = cnt + len(sent) + len(SEPARATOR)
                if original_idx >= new_cnt:
                    cnt = new_cnt
                    continue
                offset = original_idx - cnt
                return _us.id.get_sid(sidx), offset
        raise KeyError

    def get_groups(self, uttrs: Utterances) -> List[SpanGroup]:
        offset_sid = self.get_offset_sid()
        offset_sent = self.get_offset_sentence()
        offset_scud = self.get_offset_scud()
        assert offset_sent < offset_scud

        groups: List[SpanGroup] = []
        label2gidx: Dict[str, int] = {}
        for ant in self.labels:
            s: int = int(ant[0])
            e: int = int(ant[1])
            label = str(ant[2])
            sid: SID
            is_target: bool
            if s < offset_sid:
                sid_s, s = self.get_sid_and_offset(s, uttrs)
                sid_e, e = self.get_sid_and_offset(e, uttrs)
                assert sid_s == sid_e, f"{sid_s} != {sid_e}"
                sid = sid_s
                is_target = False
            else:
                if s < offset_scud:
                    sid = self.get_sid()
                    s -= offset_sent
                    e -= offset_sent
                    is_target = False
                    mytext = self.get_sentence()
                else:
                    sid = self.get_sid()
                    s -= offset_scud
                    e -= offset_scud
                    is_target = True
                    mytext = self.get_scud_text()
                if label != "エラー":
                    if not (0 <= s <= len(mytext)) or not (0 <= e <= len(mytext)):
                        raise KeyError(f"Invalid offset: {ant} for {self.text}")

            span = Span(is_target=is_target, start=s, end=e, sid=sid)
            gidx = label2gidx.get(label)
            _gt = label2group_type(label)
            if gidx is None:
                groups.append(SpanGroup(group_type=_gt, spans=[span]))
                label2gidx[label] = len(groups) - 1
            else:
                groups[gidx].spans.append(span)
        for g in groups:
            if g.group_type == GroupType.OUTSIDE and len(set(s.sid for s in g.spans)) == 1:
                g.group_type = GroupType.EXOPHORA
            g.spans.sort()
            vals = [v.json() for v in g.spans]
            assert len(set(vals)) == len(vals), f"Duplicated spans in: {g.spans}"
        groups.sort()
        return groups


class TrimmedDoccanoAnnotation(BaseModel):
    sid: SID
    idx: int
    scud: str
    groups: List[SpanGroup]

    def __lt__(self, other) -> bool:
        if self.sid != other.sid:
            return self.sid < other.sid
        return self.idx < other.idx


def get_temporary_groups(src: str, scud: str, sid: SID) -> List[SpanGroup]:
    scud_no_lastdot = scud.rstrip("。")
    s = difflib.SequenceMatcher(None, src, scud_no_lastdot)
    groups: List[SpanGroup] = []

    for (op, a_0, a_1, b_0, b_1) in s.get_opcodes():
        if op == "replace":
            continue
        elif op == "insert":
            continue
        elif op == "delete":
            continue

        spans = [
            Span(is_target=False, start=a_0, end=a_1, sid=sid),
            Span(is_target=True, start=b_0, end=b_1, sid=sid),
        ]
        group = SpanGroup(
            group_type=GroupType.INSIDE,
            spans=spans,
        )
        groups.append(group)
    return groups


def convert_one(scud: Scud, uttrs: Utterances):
    _src = scud.text
    _scud = scud.scud
    if len(scud.groups) == 0:
        scud.groups = get_temporary_groups(_src, _scud, scud.sid)

    sid = scud.sid

    context: str = SEPARATOR.join(uttrs.get_contexts(sid=sid, same_uttr=True, by_uttr=False))

    out_text = context + SEPARATOR + scud.id + SEPARATOR + _src + SEPARATOR + _scud
    labels = []
    label_idx_in = 0
    label_idx_both = 0
    label_idx_out = 0
    offset_scud = len(out_text) - len(_scud)
    offset_src = offset_scud - len(SEPARATOR) - len(_src)

    for grp in scud.groups:
        if grp.group_type == GroupType.INSIDE:
            _str_label = f"{label_idx_in}"
            label_idx_in += 1
        elif grp.group_type == GroupType.BOTHSIDE:
            _str_label = f"{PREFIX_BOTHSIDE}{label_idx_both}"
            label_idx_both += 1
        elif grp.group_type in {GroupType.OUTSIDE, GroupType.EXOPHORA}:
            _str_label = f"{PREFIX_OUTSIDE}{label_idx_out}"
            label_idx_out += 1
        else:
            raise NotImplementedError

        for span in grp.spans:
            _offset: int = 0
            if span.is_target:
                _offset = offset_scud
            else:
                if span.sid == sid:
                    _offset = offset_src
                else:
                    _ctx: List[str] = uttrs.get_contexts(sid=span.sid, same_uttr=True, by_uttr=False)
                    _offset = len(SEPARATOR.join(_ctx) + SEPARATOR)
            labels.append([span.start + _offset, span.end + _offset, _str_label])
    labels.sort()
    assert len(labels) == len(set([tuple(v) for v in labels])), f"Duplication in {sid}:{labels}"

    return {"text": out_text, "labels": labels, "meta": {"sid": sid.id, "idx": scud.idx}}


def convert(
    path_in: Path,
    path_ref: Path,
    path_use: Optional[Path],
) -> Iterator[str]:
    assert path_in.is_dir()
    d2u = Docid2Utterances(path_ref)

    def get_key(one):
        meta = one["meta"]
        return (meta["sid"], meta["idx"])

    for docid, uttrs in d2u.items():
        cache = {}
        if path_use is not None:
            with list(path_use.glob(f"{docid.doc_num_str}.*"))[0].open() as inf:
                for line in inf:
                    scud = Scud.parse_raw(line)
                    one = convert_one(scud, uttrs)
                    cache[get_key(one)] = one

        with list(path_in.glob(f"{docid.doc_num_str}.*"))[0].open() as inf:
            for line in inf:
                scud = Scud.parse_raw(line)
                one = convert_one(scud, uttrs)
                key = get_key(one)
                out_one = cache.get(key, one)
                yield json.dumps(out_one, ensure_ascii=False, sort_keys=True)


Sid2Annotations = NewType("Sid2Annotations", Dict[SID, List[TrimmedDoccanoAnnotation]])


def _open_doccano(rfname: Path) -> Sid2Annotations:
    assert rfname.is_dir()

    sid2annotations: Sid2Annotations = Sid2Annotations({})
    for _rfp in rfname.iterdir():
        with _rfp.open() as rf:
            for rline in rf:
                onedata = TrimmedDoccanoAnnotation.parse_raw(rline)
                sid = onedata.sid
                if sid not in sid2annotations:
                    sid2annotations[sid] = []
                sid2annotations[sid].append(onedata)
    return sid2annotations


def update_json(sid2scuds: Sid2Scuds, sid2annotations: Sid2Annotations) -> Iterator[str]:

    for sid, scuds in sorted(sid2scuds.items()):
        annotations = sorted(sid2annotations[sid])
        scuds = sorted(scuds)
        assert len(scuds) == len(annotations), f"In {sid}: {len(scuds)} != {len(annotations)}"
        for scud, annotation in zip(scuds, annotations):
            assert scud.idx == annotation.idx, f"In {sid}: Idx mismatch"
            scud.scud = annotation.scud
            yield scud.json(ensure_ascii=False, sort_keys=True)


def parse_doccano(sid2scuds: Sid2Scuds, sid2annotations: Sid2Annotations, ref: Path) -> Iterator[Scud]:
    d2u = Docid2Utterances(ref)

    found_error: bool = False
    for sid, scuds in sorted(sid2scuds.items()):
        annotations: List[TrimmedDoccanoAnnotation] = []
        try:
            annotations = sorted(sid2annotations[sid])
        except IndexError:
            sys.stderr.write(f"Annotation document error: {sid}\n")
            found_error = True
        scuds = sorted(scuds)

        annotation: TrimmedDoccanoAnnotation
        for scud, annotation in zip_longest(scuds, annotations):
            if scud is None or annotation is None:
                sys.stderr.write("Data size mismatch:\n")
                _s = None
                if annotation:
                    _s = annotation.scud
                sys.stderr.write(f"\t{scud}\n\t{_s}\n\n")
                found_error = True
                continue
            assert scud.sid == annotation.sid == sid
            assert scud.idx == annotation.idx
            _sent = d2u[sid.docid].get(sid=sid)
            if len(scud.text) != len(_sent):
                sys.stderr.write(f"Length mismatch: {scud.id}\n" f"\t{scud.text}" f"\t{_sent}\n")
                found_error = True
            if scud.scud != annotation.scud:
                sys.stderr.write(f"Scud mismatch: {scud.id}\n" f"\t{scud.scud}\n" f"\t{annotation.scud}\n")
                found_error = True

            scud.groups = annotation.groups
            found_error |= not check_scud_groups(scud)
            yield scud
    if found_error:
        raise ValueError


def trim(inpath: Path, ref: Path, outpath: Path):
    outpath.mkdir(exist_ok=True, parents=True)

    d2u = Docid2Utterances(ref)
    docid2outs = {}
    with inpath.open() as inf:
        for inline in inf:
            onedata: DoccanoAnnotation = DoccanoAnnotation.parse_raw(inline)
            sid: SID = onedata.get_sid()
            assert onedata.meta["sid"] == sid.id
            idx = onedata.get_idx()
            assert onedata.meta["idx"] == idx
            myuttrs = d2u[sid.docid]

            out = TrimmedDoccanoAnnotation(
                sid=sid,
                idx=idx,
                scud=onedata.get_scud_text(),
                groups=onedata.get_groups(myuttrs),
            )
            if sid.docid.doc_num_str not in docid2outs:
                docid2outs[sid.docid.doc_num_str] = []
            docid2outs[sid.docid.doc_num_str].append(out)

        for docid, outs in docid2outs.items():
            with outpath.joinpath(f"{docid}.TrimmedDoccanoAnnotation.jsonl").open("w") as outf:
                for out in sorted(outs):
                    outf.write(out.json(sort_keys=True, ensure_ascii=False))
                    outf.write("\n")


def output_final_scud(
    sid2scuds,
    sid2annotations,
    path_ref: Path,
    path_out: Path,
):
    docidstr2scuds: DefaultDict[str, List[Scud]] = defaultdict(list)
    for sa in parse_doccano(sid2scuds, sid2annotations, path_ref):
        docidstr: str = sa.sid.docid.doc_num_str
        docidstr2scuds[docidstr].append(sa)
    for docidstr, scuds in docidstr2scuds.items():
        with path_out.joinpath(f"{docidstr}.jsonl").open("w") as outf:
            for scud in sorted(scuds):
                outf.write(scud.json(sort_keys=True, ensure_ascii=False))
                outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--trim", action="store_true")
    oparser.add_argument("--result", "-r", type=Path)
    oparser.add_argument("--update", action="store_true")

    oparser.add_argument("--ref", type=Path, required=True)
    oparser.add_argument("--use", type=Path)
    return oparser.parse_args()


def main():
    opts = get_opts()
    if opts.trim:
        trim(opts.input, opts.ref, opts.output)
    elif opts.result:
        sid2scuds = open_scud_file(opts.input)
        sid2annotations = _open_doccano(opts.result)
        if len(sid2scuds) != len(sid2annotations):
            v = set(sid2scuds.keys()) ^ set(sid2annotations.keys())
            sys.stderr.write(f"Not exist in another: {sorted(list(v))}\n")
            sys.exit(1)

        if opts.update:
            with opts.output.open("w") as outf:
                for line in update_json(sid2scuds, sid2annotations):
                    outf.write(f"{line}\n")
        else:
            try:
                output_final_scud(sid2scuds, sid2annotations, opts.ref, opts.output)
            except ValueError:
                sys.exit(1)

    else:
        with opts.output.open("w") as outf:
            for line in convert(opts.input, opts.ref, opts.use):
                outf.write(f"{line}\n")


if __name__ == "__main__":
    main()
