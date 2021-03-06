#!/usr/bin/env python3

import argparse
import collections
import csv
import sys
import typing
import unicodedata
from pathlib import Path
from typing import DefaultDict, Optional, Tuple

from asdc.schema.dialog import GroupType, Scud, Utterances, open_scud_file_by_docid
from asdc.schema.example import METACHAR_LINE_BREAK, METACHAR_SENTENCE_BOUNDARY, Example
from asdc.schema.id import SID

DATA_TYPES: typing.List[str] = ["setting", "qa", "text", "scud_main", "scud_json", "example", "vanilla"]


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", required=True, type=Path)
    oparser.add_argument("--type", "-t", choices=DATA_TYPES, required=True)
    oparser.add_argument("--ref", type=Path)
    return oparser.parse_args()


def check_setting(inf) -> bool:
    r = csv.reader(inf)
    for lid, items in enumerate(r):
        if len(items) != 7:
            print(f"Invalid length: {len(items)} on line {lid}")
            return False
    return True


def check_qa(inf) -> bool:
    r = csv.reader(inf)
    for lid, items in enumerate(r):
        if len(items) != 10:
            print(f"Invalid length: {len(items)} on line {lid}")
            return False
    return True


def check_text(inpath: Path, ref: Path) -> bool:
    for fname in inpath.iterdir():
        path_json: Path = ref.joinpath(fname.stem + ".json")
        uttrs = Utterances.parse_file(path_json)

        with fname.open() as inf:
            for lid, line in enumerate(inf):
                items = line[:-1].split("\t", maxsplit=1)
                item1 = items[1].replace(METACHAR_SENTENCE_BOUNDARY, "")
                text: str = uttrs.utterances[lid].text.replace("\n", METACHAR_LINE_BREAK)
                if items[0] != uttrs.utterances[lid].name or item1 != text:
                    print(f"Invalid data: Line {lid} in {fname}")
                    return False
                if unicodedata.normalize("NFKC", text) != text:
                    print(f"Not NFKC: Line {lid} in {fname}")
                    return False

    return True


def check_scud_groups(scud: Scud) -> bool:
    assert scud.groups is not None
    _target_annotated_idxs = set()
    for group in scud.groups:
        _source_text_found = False
        _target_text_found = False
        for span in group.spans:
            if span.is_target:
                for v in range(span.start, span.end):
                    _target_annotated_idxs.add(v)
                _target_text_found = True
            else:
                _source_text_found = True

        if not _target_text_found:
            sys.stderr.write(f"Target text does not exist in a group ({scud.sid.id})" f": {group.spans}\n")
            return False
        if not _source_text_found and group.group_type == GroupType.INSIDE:
            sys.stderr.write("Matched source text does not exist" f" in {scud.sid.id}: {group.spans}\n")
            return False

    for idx, char in enumerate(scud.scud):
        if idx in _target_annotated_idxs:
            continue
        elif char in ["???", "???", "???", " "]:
            continue
        sys.stderr.write(f"Target character on idx={idx} in {scud.sid.id}" " is not annotated\n")
        return False
    return True


def check_scud_main(inpath: Path, ref: Path) -> bool:
    docid2scuds = open_scud_file_by_docid(inpath)
    ok = True
    for docid, scuds in sorted(docid2scuds.items()):
        path_json: Path = ref.joinpath(f"{docid.doc_num_str}.json")
        uttrs = Utterances.parse_file(path_json)

        _all_queriers: DefaultDict[str, int] = collections.defaultdict(int)
        _num_representative: DefaultDict[str, int] = collections.defaultdict(int)
        for _s in scuds:
            if _s.text != uttrs.get(sid=_s.sid):
                print(f"Invalid text in {_s.sid.id}:\n" f"\t{_s.text}\n\t{uttrs.get(sid=_s.sid)}")
                return False

            if _s.scud != unicodedata.normalize("NFKC", _s.scud):
                print(f"Not normalized scud for {_s.sid.id}")
                return False

            ok &= check_scud_groups(_s)
            for _q in _s.queries:
                mark = ""
                if _q[0] in "@???":
                    mark = _q[0]
                    _q = _q[1:]
                if mark == "@":
                    if len(_q) != 0:
                        print(f"Needless characters in {_s.sid.id}: {_q}")
                        ok = False
                else:
                    if _q not in uttrs.meta.conditions:
                        print(f"Invalid query: {_q}")
                        ok = False
                    _all_queriers[_q] += 1
                    if mark == "???":
                        _num_representative[_q] += 1

            if len(set(_s.queries)) != len(_s.queries):
                print(f"Duplicated queries in {_s.sid.id}: {_s.queries}")
                ok = False

        for _q, _num in _all_queriers.items():
            if _num > 1:
                if _num_representative[_q] == 0:
                    print(f"Not found ??? in {docid.id}: {_q}")
                    ok = False
            #                 elif _num_representative[_q] > 1:
            #                     print(f'Too many ??? in {docid.id}: {_q}')
            #                     ok = False
            else:
                if _num_representative[_q] != 0:
                    print(f"Invalid number of ??? in {docid.id}: {_q}")
                    ok = False

        scud_idxs: DefaultDict[Tuple[SID, int], int] = collections.defaultdict(int)
        for _s in scuds:
            scud_idxs[(_s.sid, _s.idx)] += 1
        for (sid, idx), cnt in scud_idxs.items():
            if cnt != 1:
                print(f"Duplicated idx in {sid.id}: {idx}")
                ok = False

    return ok


def check_scud_json(inpath: Path) -> bool:
    import json

    ok = True
    for fname in sorted(inpath.iterdir()):
        data = fname.open().read()
        _ = Utterances.parse_raw(data)
        fdata = json.dumps(json.loads(data), indent=4, ensure_ascii=False, sort_keys=True) + "\n"
        if data != fdata:
            print(f"Unformatted JSON: {fname}")
            ok = False
    return ok


def check_example(inpath: Path) -> bool:
    import json

    ok = True
    for fname in sorted(inpath.glob("*.jsonl")):
        with fname.open() as inf:
            for line in inf:
                _ = Example.parse_raw(line)
                fdata = json.dumps(json.loads(line), ensure_ascii=False, sort_keys=True) + "\n"
                if line != fdata:
                    print(f"Unformatted JSON: {fname}")
                    ok = False
    return ok


def check_vanilla(inpath: Path) -> bool:
    import json

    from asdc.schema.vanilla import VanillaUtterances

    ok = True
    for fname in sorted(inpath.glob("*.jsonl")):
        with fname.open() as inf:
            for line in inf:
                _ = VanillaUtterances.parse_raw(line)
                fdata = json.dumps(json.loads(line), ensure_ascii=False, sort_keys=True) + "\n"
                if line != fdata:
                    print(f"Unformatted JSON: {fname}")
                    ok = False
    return ok


def check(inpath: Path, typename: str, ref: Optional[Path]) -> bool:
    ok = True
    if typename == DATA_TYPES[0]:
        with open(inpath) as inf:
            ok &= check_setting(inf)
    elif typename == DATA_TYPES[1]:
        raise NotImplementedError
    elif typename == DATA_TYPES[2]:
        assert ref is not None
        ok &= check_text(inpath, ref)
    elif typename == DATA_TYPES[3]:
        assert ref is not None
        ok &= check_scud_main(Path(inpath), ref)
    elif typename == DATA_TYPES[4]:
        ok &= check_scud_json(inpath)
    elif typename == DATA_TYPES[5]:
        ok &= check_example(inpath)
    elif typename == DATA_TYPES[6]:
        ok &= check_vanilla(inpath)

    else:
        print(f"Invalid typename: {typename}")
        return False

    return ok


def main() -> None:
    opts = get_opts()
    ok = check(opts.input, opts.type, opts.ref)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
