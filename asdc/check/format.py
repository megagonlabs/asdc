#!/usr/bin/env python3

import argparse
import collections
import csv
import json
import sys
import typing
import unicodedata
from pathlib import Path
from typing import Callable, DefaultDict, Dict, Optional, Set, Tuple

from asdc.schema.dialog import GroupType, Scud, Utterances, open_scud_file_by_docid
from asdc.schema.example import METACHAR_LINE_BREAK, METACHAR_SENTENCE_BOUNDARY, METAKEY_INCORRECT, Example
from asdc.schema.id import SID, DocID, UttrID
from asdc.schema.vanilla import VanillaUtterances


def check_setting(inpath: Path, ref: Optional[Path]) -> bool:
    assert ref is None
    with open(inpath) as inf:
        r = csv.reader(inf)
        for lid, items in enumerate(r):
            if len(items) != 7:
                print(f"Invalid length: {len(items)} on line {lid}")
                return False
    return True


def check_text(inpath: Path, ref: Optional[Path]) -> bool:
    assert ref is not None
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
        elif char in ["、", "。", "　", " "]:
            continue
        sys.stderr.write(f"Target character on idx={idx} in {scud.sid.id}" " is not annotated\n")
        return False
    return True


def check_scud_main(inpath: Path, ref: Optional[Path]) -> bool:
    assert ref is not None

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
                if _q[0] in "@★":
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
                    if mark == "★":
                        _num_representative[_q] += 1

            if len(set(_s.queries)) != len(_s.queries):
                print(f"Duplicated queries in {_s.sid.id}: {_s.queries}")
                ok = False

        for _q, _num in _all_queriers.items():
            if _num > 1:
                if _num_representative[_q] == 0:
                    print(f"Not found ★ in {docid.id}: {_q}")
                    ok = False
            #                 elif _num_representative[_q] > 1:
            #                     print(f'Too many ★ in {docid.id}: {_q}')
            #                     ok = False
            else:
                if _num_representative[_q] != 0:
                    print(f"Invalid number of ★ in {docid.id}: {_q}")
                    ok = False

        scud_idxs: DefaultDict[Tuple[SID, int], int] = collections.defaultdict(int)
        for _s in scuds:
            scud_idxs[(_s.sid, _s.idx)] += 1
        for (sid, idx), cnt in scud_idxs.items():
            if cnt != 1:
                print(f"Duplicated idx in {sid.id}: {idx}")
                ok = False

    return ok


def check_scud_json(inpath: Path, ref: Optional[Path]) -> bool:
    assert ref is None

    ok = True
    for fname in sorted(inpath.iterdir()):
        data = fname.open().read()
        _ = Utterances.parse_raw(data)
        fdata = json.dumps(json.loads(data), indent=4, ensure_ascii=False, sort_keys=True) + "\n"
        if data != fdata:
            print(f"Unformatted JSON: {fname}")
            ok = False
    return ok


def check_example(inpath: Path, ref: Optional[Path], acceptable_sid_prefix: str) -> bool:
    docid2vus: Optional[Dict[DocID, VanillaUtterances]] = None
    user_uttr_ids: Optional[Set[UttrID]] = None
    if ref is not None:
        docid2vus = {}
        user_uttr_ids = set()
        for f in ref.iterdir():
            with f.open() as inf:
                for line in inf:
                    vus = VanillaUtterances.parse_raw(line)
                    if vus.docid in docid2vus:
                        raise KeyError(f"Duplicated ID: {vus.docid}")
                    docid2vus[vus.docid] = vus

                    for idx, vu in enumerate(vus.utterances):
                        if vu.name == "user":
                            uttrid = UttrID(id=f"{vus.docid.id}.{idx}")
                            assert uttrid.docid == vus.docid, (uttrid, vus.docid)
                            user_uttr_ids.add(uttrid)
    assert inpath.is_dir()

    ok = True
    for fname in sorted(inpath.glob("**/*.jsonl")):
        with fname.open() as inf:
            for line in inf:
                ex = Example.parse_raw(line)
                if not ex.sid.id.startswith(acceptable_sid_prefix):
                    print(f"Unacceptable SID: {ex.sid.id}")
                    ok = False
                elif (
                    user_uttr_ids is not None
                    and "incorrect" not in ex.sid.id
                    and (ex_uttrtid := ex.sid.uttrid) not in user_uttr_ids
                ):
                    print(f"Unacceptable UttrID: {ex_uttrtid.id} (in SID={ex.sid.id})")
                    ok = False

                fdata = json.dumps(json.loads(line), ensure_ascii=False, sort_keys=True) + "\n"
                if line != fdata:
                    print(f"Unformatted JSON: {fname}")
                    ok = False

                if docid2vus is None:
                    continue
                vus = docid2vus.get(ex.sid.docid)
                if vus is None:
                    print(f"Unknown docid: {ex.sid.docid} (ex.sid) for {ex} in {fname}")
                    ok = False
                    continue
                if vus.purpose != ex.purpose:
                    print(f"Wrong purpose: {ex} (not {vus.purpose}")
                    ok = False
                    continue

                org_text: str = vus.utterances[ex.sid.uttrid.num].text
                if (ex_src := "".join(ex.sources)) != org_text:
                    print(f"Invalid sources ({ex.sid}) / {org_text} / {ex_src}")
                    ok = False
                    continue

                if len(ex.context) != ex.sid.uttrid.num:
                    print(f"Invalid length of context ({ex.sid})")
                    ok = False
                    continue
                for ctx, exctx in zip(ex.context, vus.utterances[: ex.sid.uttrid.num]):
                    if ctx.name != exctx.name:
                        print(f"Invalid name of context ({ex.sid})")
                        ok = False
                    elif ctx.text != exctx.text:
                        print(f"Invalid text of context ({ex.sid})")
                        ok = False

    return ok


def check_vanilla(inpath: Path, ref: Optional[Path]) -> bool:
    assert inpath.is_dir()
    assert ref is None
    done_ids = set()

    from asdc.schema.vanilla import VanillaUtterances

    ok = True
    for fname in sorted(inpath.glob("**/*.jsonl")):
        with fname.open() as inf:
            for line in inf:
                vus = VanillaUtterances.parse_raw(line)
                if vus.docid in done_ids:
                    print(f"Duplicated ID: {vus.docid}")
                    ok = False
                else:
                    done_ids.add(vus.docid)

                fdata = json.dumps(json.loads(line), ensure_ascii=False, sort_keys=True) + "\n"
                if line != fdata:
                    print(f"Unformatted JSON: {fname}")
                    ok = False
    return ok


def check_incorrect_example_meta(ex: Example) -> bool:
    if METAKEY_INCORRECT not in ex.meta:
        print("Key incorrect does not exist")
        return False

    k = ex.meta[METAKEY_INCORRECT]
    if k is None or isinstance(k, bool):
        pass
    else:
        print("Invalid type of value")
        return False
    return True


def check_incorrect_example(inpath: Path, ref: Optional[Path]) -> bool:
    assert inpath.is_dir()
    assert ref is not None

    ok: bool = True
    sid2ex: Dict[str, Example] = {}
    done_sids = set()

    for fname in sorted(ref.glob("**/*.jsonl")):
        with fname.open() as inf:
            for line in inf:
                ex = Example.parse_raw(line)
                assert ex.sid.id not in sid2ex, ex.sid.id
                sid2ex[ex.sid.id] = ex
                if ex.sid.id in done_sids:
                    ok = False
                    print(f"Duplicated SID: {ex.sid.id}")
                done_sids.add(ex.sid.id)

    for fname in sorted(inpath.glob("**/*.jsonl")):
        with fname.open() as inf:
            for line in inf:
                ex = Example.parse_raw(line)

                if ex.sid.id in done_sids:
                    ok = False
                    print(f"Duplicated SID: {ex.sid.id}")
                done_sids.add(ex.sid.id)

                ok &= check_incorrect_example_meta(ex)

                original_doc_id = ex.meta.get("original")
                if original_doc_id is None:
                    continue

                original_ex = sid2ex.get(original_doc_id)
                if original_ex is None:
                    print(f"Unknown original ID: {original_doc_id}, {ex}")
                    ok = False
                else:
                    if original_ex.context != ex.context:
                        print(f"Mismatch context: {original_doc_id}", original_ex, ex)
                        ok = False
                    if original_ex.sources != ex.sources:
                        print(f"Mismatch sources: {original_doc_id}", original_ex.sources, ex.sources)
                        #                         print(f"Mismatch sources: {original_doc_id}", original_ex, ex)
                        ok = False
                    if original_ex.targets == ex.targets:
                        print(f"Same targets: {original_doc_id}", original_ex, ex)
                        ok = False
    return ok


DATA_TYPES: typing.Dict[str, Callable] = {
    "setting": check_setting,
    "text": check_text,
    "scud_main": check_scud_main,
    "scud_json": check_scud_json,
    "incorrect_example": check_incorrect_example,
    "vanilla": check_vanilla,
}


def check(inpath: Path, typename: str, ref: Optional[Path], acceptable_sid_prefix: Optional[str]) -> bool:
    if typename == "example":
        assert acceptable_sid_prefix is not None
        return check_example(inpath, ref, acceptable_sid_prefix)

    func = DATA_TYPES.get(typename)
    if func is None:
        print(f"Invalid typename: {typename}")
        return False
    return func(inpath, ref)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", required=True, type=Path)
    oparser.add_argument("--type", "-t", choices=list(DATA_TYPES.keys()) + ["example"], required=True)
    oparser.add_argument("--ref", type=Path)
    oparser.add_argument("--prefix")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    ok = check(opts.input, opts.type, opts.ref, opts.prefix)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
