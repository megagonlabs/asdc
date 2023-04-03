#!/usr/bin/env python3

import argparse
import random
from pathlib import Path

from asdc.schema.example import Example, VanillaUtterance
from asdc.schema.id import SID


class SidGenerator:
    def __init__(self):
        self.idx = 0

    def get(self) -> str:
        self.idx += 1
        return f"correctness_labeled.auto_scud.{self.idx:05}.1-0"


def gen(
    correct: bool,
    price: int,
    use_comma: bool,
    _g: SidGenerator,
    purpose: str,
) -> str:
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
    gold: str = f"予算は{price}円だ。"
    if not correct:
        ngprice: int = price
        if bool(random.getrandbits(1000)):
            ngprice += random.randint(1, 500)
        else:
            ngprice += random.randint(-500, -1)
        gold = f"予算は{ngprice}円だ。"

    example_types = None
    if not correct:
        example_types = ["untruth"]
    ex = Example(
        sid=SID(id=_g.get()),
        correct=correct,
        context=[
            VanillaUtterance(
                name="agent",
                text=q,
            ),
        ],
        sources=[ans],
        targets=[gold],
        purpose=purpose,  # type: ignore
        meta={},
        example_types=example_types,  # type: ignore
        original_sid=None,
    )
    return ex.json(ensure_ascii=False, sort_keys=True) + "\n"


def operation(
    *,
    path_out: Path,
) -> None:
    purposes = ["dev"] + ["test"] + ["train"] * 8

    _g = SidGenerator()

    with path_out.open("w") as outf:
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

                    for isok in [True, False]:
                        outf.write(
                            gen(
                                isok,
                                price,
                                use_comma,
                                _g,
                                purpose,
                            )
                        )


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(
        path_out=opts.output,
    )


if __name__ == "__main__":
    main()
