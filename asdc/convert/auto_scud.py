#!/usr/bin/env python3

import argparse
import copy
import random
from pathlib import Path

from asdc.schema.example import Example, VanillaUtterance, VanillaUtterances
from asdc.schema.id import SID


def operation(
    *,
    path_out: Path,
) -> None:
    purposes = ["dev"] + ["test"] + ["train"] * 8

    idx: int = 0

    path_out.mkdir(exist_ok=True, parents=True)
    path_out_correct = path_out.joinpath("auto_number.jsonl")
    path_out_ok_scud = path_out.joinpath("auto_number.Example.jsonl")
    path_out_vanilla = path_out.joinpath("auto_number.VanillaUtterances.jsonl")
    with path_out_correct.open("w") as outf_correct, path_out_vanilla.open("w") as outf_vanilla, path_out_ok_scud.open(
        "w"
    ) as outf_scud:
        for k in range(1, 40):
            for use_comma in [False, True]:
                for diff in [
                    0,
                    random.randint(-500, 0),
                    random.randint(0, 500),
                    random.randint(-5, 0),
                    random.randint(0, 5),
                ]:
                    purpose: str = random.choice(purposes)
                    price: int = k * 1000 - diff

                    price_str: str = f"{price}"
                    if use_comma:
                        price_str = f"{price:,}"

                    tail: str = random.choice(["", "。", "です。"])
                    q: str = random.choice(
                        [
                            "ご予算はいくらですか?",
                        ]
                    )
                    ans: str = f"{price_str}円{tail}"

                    original_sid = SID(id=f"asdc.sup.auto_number.{idx:05}.1-0")
                    docid = original_sid.docid
                    csid0 = SID(id=f"correctness_labeled.asdc.auto_number.{idx:05}.1-0")
                    idx += 1

                    # vanilla
                    gold_text: str = f"予算は{price}円だ。"
                    vus_list = [
                        VanillaUtterance(
                            name="agent",
                            text=q,
                        ),
                        VanillaUtterance(
                            name="user",
                            text=ans,
                        ),
                    ]

                    vus = VanillaUtterances(
                        docid=docid,
                        purpose=purpose,  # type: ignore
                        meta={},
                        utterances=vus_list,
                    )
                    outf_vanilla.write(vus.json(ensure_ascii=False, sort_keys=True) + "\n")

                    # OK
                    ex_gold = Example(
                        sid=original_sid,
                        correct=True,
                        context=[
                            vus_list[0],
                        ],
                        sources=[ans],
                        targets=[gold_text],
                        purpose=purpose,  # type: ignore
                        meta={
                            "gold_price": price,
                        },
                        example_types=None,  # type: ignore
                        original_sid=None,
                    )
                    outf_scud.write(ex_gold.json(ensure_ascii=False, sort_keys=True) + "\n")

                    # NG
                    ngprice: int = price
                    if bool(random.getrandbits(1000)):
                        ngprice += random.randint(1, 500)
                    else:
                        ngprice += random.randint(-500, -1)
                    ng_text: str = f"予算は{ngprice}円だ。"

                    ex_ng = copy.deepcopy(ex_gold)
                    ex_ng.sid = csid0
                    ex_ng.correct = False
                    ex_ng.targets = [ng_text]
                    ex_ng.example_types = ["untruth"]
                    outf_correct.write(ex_ng.json(ensure_ascii=False, sort_keys=True) + "\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--output", "-o", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_out=opts.output,
    )


if __name__ == "__main__":
    main()
