#!/usr/bin/env python3

import argparse
import collections
import statistics
from pathlib import Path
from typing import Optional

from asdc.schema.dialog import GroupType, Scud, Utterances
from asdc.schema.example import Example
from asdc.schema.id import SID


class DataStore(list):
    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        super(DataStore, self).__init__(*args, **kwargs)

    def stat(self) -> str:
        return f"""{self.name}
\tSize={len(self)}
\tSum={sum(self)}
\tAVG={statistics.mean(self)}
\tMED={statistics.median(self)}
\tVAR={statistics.variance(self)}
\tMin={min(self)}
\tMax={max(self)}
"""


def stat_dialogs(path_in: Path):
    num_uttrs = DataStore("Utterances")
    num_sents = DataStore("Sentences")
    num_sents_c = DataStore("Sentences_user")
    num_sents_o = DataStore("Sentences_agent")
    for fpath in sorted(path_in.iterdir()):
        uttrs = Utterances.parse_file(fpath)
        uttr_cnt = 0
        prev_user = ""
        for u in uttrs.utterances:
            if u.name != prev_user:
                uttr_cnt += 1
                prev_user = u.name
            _s0 = len(u.text_sbs)
            if u.name.startswith("user_"):
                num_sents_c.append(_s0)
            else:
                num_sents_o.append(_s0)

        num_uttrs.append(uttr_cnt)
        _s = sum([len(u.text_sbs) for u in uttrs.utterances])
        num_sents.append(_s)

    for v in [num_uttrs, num_sents, num_sents_c, num_sents_o]:
        print(v.stat())


def get_uttr_distance(scud: Scud) -> int:
    uttr_ids = set()
    for sg in scud.groups:
        if sg.group_type == GroupType.EXOPHORA:
            continue
        for _span in sg.spans:
            uttr_ids.add(_span.sid.uttrid)

    assert len(uttr_ids) > 0
    max_distance_uttr: int = max(uttr_ids) - min(uttr_ids)
    return max_distance_uttr


def get_internal_sentence_distance(scud: Scud) -> Optional[int]:
    internal_sids: set[SID] = set()
    for sg in scud.groups:
        for _span in sg.spans:
            if len(sg.spans) > 1 and _span.sid.uttrid == scud.sid.uttrid:
                internal_sids.add(_span.sid)

    max_distance_sentence: Optional[int] = None
    if len(internal_sids) > 0:
        max_distance_sentence = max(internal_sids) - min(internal_sids)  # type: ignore
    return max_distance_sentence


def stat_example(path_in_dir_or_file: Path):
    docids = set()
    uttrids = set()
    sids = set()

    if path_in_dir_or_file.is_dir():
        path_list = [path_in for path_in in path_in_dir_or_file.iterdir()]
    else:
        path_list = [path_in_dir_or_file]

    for path_in in path_list:
        with path_in.open() as inf:
            for line in inf:
                ex = Example.model_validate_json(line)
                assert ex.sid not in sids

                docids.add(ex.sid.docid)
                uttrids.add(ex.sid.uttrid)
                sids.add(ex.sid)
    print(f"# of Doc: {len(docids):,}")
    print(f"# of Uttr: {len(uttrids):,}")
    print(f"# of sentences: {len(sids):,}")


def stat_scud(path_in: Path):
    num_query_match = DataStore("ScudMatch")
    num_query_non_match = DataStore("ScudNonMatch")
    num_query_lack = 0
    num_query_imcomlete_match = 0
    total = 0
    num_uttr_distance = DataStore("AlignmentUttrDiscante")
    num_sent_distance = DataStore("AlignmentSentenceDiscante")
    with path_in.open() as inf:
        for line in inf:
            total += 1
            scud = Scud.model_validate_json(line)
            max_distance_uttr: int = get_uttr_distance(scud)
            num_uttr_distance.append(max_distance_uttr)
            max_distance_sent: Optional[int] = get_internal_sentence_distance(scud)
            num_sent_distance.append(max_distance_sent)

            if len(scud.queries) == 0:
                num_query_non_match.append(1)
            elif scud.queries == ["@"]:
                num_query_non_match.append(1)
                num_query_lack += 1
            else:
                size = len(scud.queries)
                if "@" in scud.queries:
                    size -= 1
                    num_query_imcomlete_match += 1
                num_query_match.append(size)

    print(f"Total: {total}")
    print()
    print("--- query ---")
    print(num_query_match.stat())
    c = collections.Counter(num_query_match)
    print(c)
    print(num_query_non_match.stat())
    print(f"num_query_lack\t{num_query_lack}")
    print(f"num_query_imcomlete_match\t{num_query_imcomlete_match}")

    print()
    print("--- alignment ---")
    c = collections.Counter(num_uttr_distance)
    print(num_uttr_distance.stat())
    for k, v in sorted(c.items()):
        print(f"\t{k}\t{v}")
    print()

    c = collections.Counter(num_sent_distance)
    print(num_sent_distance.stat())
    for k, v in sorted(c.items()):
        print(f"\t{k}\t{v}")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--scud", action="store_true")
    oparser.add_argument("--example", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    if opts.scud:
        stat_scud(opts.input)
    elif opts.example:
        stat_example(opts.input)
    else:
        stat_dialogs(opts.input)


if __name__ == "__main__":
    main()
