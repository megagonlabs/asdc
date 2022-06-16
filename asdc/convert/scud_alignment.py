#!/usr/bin/env python3

import argparse
from pathlib import Path

from asdc.convert.split import Example


def show(path_in: Path, path_out: Path, limit_context, show: bool) -> None:
    with path_in.open() as inf, path_out.open("w") as outf:
        for line in inf:
            ex = Example.parse_raw(line)

            if show:
                for part in ex.show(limit_context=limit_context):
                    outf.write(part)
            else:
                if ex.alignments_list is None or len(ex.alignments_list) == 0:
                    continue

                for ad in ex.dump_alighment(limit_context=limit_context):
                    outf.write(ad.json(ensure_ascii=False, sort_keys=True))
                    outf.write("\n")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, default="/dev/stdin", required=False)
    oparser.add_argument("--output", "-o", type=Path, default="/dev/stdout", required=False)
    oparser.add_argument("--limit", type=int, default=1)
    oparser.add_argument("--show", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    show(opts.input, opts.output, opts.limit, opts.show)


if __name__ == "__main__":
    main()
