#!/usr/bin/env python3

import argparse
import json
from collections import defaultdict
from pathlib import Path

from asdc.schema.example import Example


def operation(path_in: Path, path_out: Path) -> None:
    text2purpose2ids = {}
    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            ex = Example.model_validate_json(line)

            for t in ex.targets:
                if t not in text2purpose2ids:
                    text2purpose2ids[t] = defaultdict(list)
                text2purpose2ids[t][ex.purpose].append(ex.sid.id)

        for text, purpose2ids in sorted(text2purpose2ids.items()):
            outf.write(f"{text}\t")
            if "test" in purpose2ids:
                outf.write("test")
            elif "dev" in purpose2ids:
                outf.write("dev")
            else:
                outf.write("train")
            outf.write("\t")

            outf.write(json.dumps(purpose2ids, sort_keys=True))
            outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.input, opts.output)


if __name__ == "__main__":
    main()
