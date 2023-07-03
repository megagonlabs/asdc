#!/usr/bin/env python3

import argparse
import csv
import json
import sys
from pathlib import Path

from asdc.check.format import check_scud_groups
from asdc.schema.dialog import open_scud_file
from asdc.schema.example import SID


def trim(sent: str, restore: bool = False) -> str:
    f2a = {
        "【customer】": "お客様",
        "【日程】": "日程",
        "【人数】": "人数",
        "【今回の旅行】": "今回の旅行",
    }
    if restore:
        f2a = {value: key for key, value in f2a.items()}
    for f, a in f2a.items():
        sent = sent.replace(f, a)

    if not restore:
        #         assert '【' not in sent, sent
        sent = sent.replace("【", "").replace("】", "")
    return sent


def update(oldscud, new: str, memo: str):
    new = new.replace("お客様", "【customer】").replace("今回の旅行", "【今回の旅行】")
    if "【日程】" in oldscud.scud:
        new = new.replace("日程", "【日程】")
    if "【人数】" in oldscud.scud:
        new = new.replace("人数", "【人数】")

    assert oldscud.scud != new, f"{oldscud.scud} != {new}"
    old: str = oldscud.scud  # tmep
    oldscud.scud = new  # update
    oldscud.memo += memo  # update

    error_idxs: list[tuple[int, int]] = []
    for gidx, grps in enumerate(oldscud.groups):
        for sidx, span in enumerate(grps.spans):
            if not span.is_target:
                continue
            new_span_text: str = span.get_text(None, new)
            old_span_text: str = span.get_text(None, old)
            if new_span_text == old_span_text:
                continue
            new_start_candidate = new.find(old_span_text)
            if new_start_candidate < 0:
                error_idxs.append((gidx, sidx))
                continue
            span.start = new_start_candidate
            span.end = new_start_candidate + len(old_span_text)

    error_groups = sorted(list(set([gidx for (gidx, _) in error_idxs])), reverse=True)
    for gidx in error_groups:
        del oldscud.groups[gidx]


def operation(path_in: Path, path_scud: Path, path_out: Path, no_same: bool) -> None:
    sid2scuds = open_scud_file(path_scud)
    sids_rewrite: set[SID] = set()
    sids_rewrite_pair: set[tuple[SID, str]] = set()

    with path_in.open() as inf, path_out.open("w") as outf:
        r = csv.reader(inf, delimiter=",")
        header = next(r)
        idx_old = header.index("SCUD")
        idx_new = header.index("修正後SCUD")
        idx_memo = header.index("メモ")
        idx_sid = header.index("文ID")
        for cols in r:
            new = cols[idx_new].strip()
            if len(new) == 0:
                continue
            assert " " not in new
            old = cols[idx_old]
            _sid = cols[idx_sid]
            assert " " not in _sid
            sid = SID(id=_sid)
            memo = cols[idx_memo]

            sids_rewrite.add(sid)
            sids_rewrite_pair.add((sid, new))

            done = False
            oldscud_target = None
            for oldscud in sid2scuds[sid]:
                oldscud_target = oldscud
                if oldscud.scud == old:
                    pass
                elif trim(oldscud.scud) == old:
                    pass
                else:
                    continue
                done = True
                break
            if not done:
                raise KeyError

            if oldscud_target:
                update(oldscud_target, new, memo)

        nun_insufficient_annotation: int = 0
        done_output: set[tuple[SID, str]] = set()
        for sid, scuds in sorted(sid2scuds.items()):
            for scud in sorted(scuds):
                if check_scud_groups(scud):
                    continue
                outf.write(json.dumps(scud.model_dump(), ensure_ascii=False, sort_keys=False))
                outf.write("\n")
                nun_insufficient_annotation += 1

                done_output.add((sid, scud.scud))
        sys.stderr.write(f"Insufficient annotation sid: {nun_insufficient_annotation}\n")

        num_rewrite: int = 0
        for sid in sorted(list(sids_rewrite)):
            for scud in sorted(sid2scuds[sid]):
                if (sid, scud.scud) not in sids_rewrite_pair:
                    continue
                elif (sid, scud.scud) in done_output:
                    continue
                outf.write(json.dumps(scud.model_dump(), ensure_ascii=False, sort_keys=False))
                outf.write("\n")
                num_rewrite += 1

        sys.stderr.write(f"Rewrite sid: {num_rewrite}\n")

        if no_same:
            return

        for sid, scuds in sorted(sid2scuds.items()):
            for scud in sorted(scuds):
                if (sid, scud.scud) in sids_rewrite_pair:
                    continue
                elif (sid, scud.scud) in done_output:
                    continue
                outf.write(json.dumps(scud.model_dump(), ensure_ascii=False, sort_keys=False))
                outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--scud", "-s", type=Path)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--nosame", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.scud, opts.output, opts.nosame)


if __name__ == "__main__":
    main()
