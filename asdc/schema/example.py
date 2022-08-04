#!/usr/bin/env python3

from typing import Any, Dict, Iterator, List, Literal, Optional, Tuple

from pydantic import BaseModel, root_validator, validator

from asdc.schema.id import SID

METACHAR_SENTENCE_BOUNDARY: str = "\u2502"
METACHAR_LINE_BREAK: str = "\u2581"


class AlignmentSpan(BaseModel):
    index: int
    start: int
    end: int

    def get_text(self, strs: List[str]) -> str:
        # strs should be "sources" if origins_in_context is False, otherwise "context"
        return strs[self.index][self.start : self.end]

    def __lt__(self, other) -> bool:
        if other.index != self.index:
            return self.index < other.index
        if other.start != self.start:
            return self.start < other.start
        return other.end < self.end

    def __hash__(self):
        return hash((self.index, self.start, self.end))


class Alignment(BaseModel):
    origins: List[AlignmentSpan]
    origins_in_context: List[bool]
    targets: List[AlignmentSpan]

    @root_validator
    def validate_source(cls, values):
        if len(values["origins"]) == len(values["origins_in_context"]):
            return values
        raise ValueError("Invalid index")


class AlignmentDump(BaseModel):
    sid: SID
    purpose: str
    origin_spans: List[str]
    target_spans: List[str]
    align: List[Tuple[int, int]]

    @validator("purpose")
    def validate_purpose(cls, v):
        if v not in ["test", "train", "dev"]:
            raise ValueError("invalid propose")
        return v


class SimpleUtterance(BaseModel):
    speaker: Literal["user", "agent"]
    text: str


class Example(BaseModel):
    sid: SID
    sources: List[str]  # List of sentences
    source_index: int  # Index of sentence in the list
    targets: List[str]
    context: List[SimpleUtterance]
    group_types: List[str]
    max_distance_uttr: int
    max_distance_sentence: Optional[int]  # SCUDの対応付けがあり，同一発話内にあるもののうち，最大で離れている文数
    meta: Dict[str, Any]
    alignments_list: Optional[List[List[Alignment]]]

    @root_validator
    def validate_source_index(cls, values):
        snum: int = values["sid"].sentence_num
        sidx: int = values["source_index"]
        if snum != sidx:
            raise ValueError(f"Mismatch between SID and source_index ({snum}, {sidx}) in {values['sid']}")
        if 0 <= sidx < len(values["sources"]):
            return values
        raise ValueError("Invalid index")

    @root_validator
    def validate_alignments_list(cls, values):
        if values["alignments_list"] is None:
            return values
        if len(values["alignments_list"]) != len(values["targets"]):
            raise ValueError("Length mismatch")

        for alignments in values["alignments_list"]:
            indices = set()
            for al in alignments:
                for t in al.targets:
                    indices.add(t.index)
            if len(indices) != 1:
                raise ValueError("Mixed target index")

        return values

    def dump_alighment(self, limit_context: int) -> Iterator[AlignmentDump]:
        if self.alignments_list is None or len(self.alignments_list) == 0:
            raise KeyError

        def _convert(
            _als: List[AlignmentSpan], sents: List[str], is_target: bool
        ) -> Tuple[List[str], Dict[AlignmentSpan, int]]:
            _spans: List[str] = []

            def _pad(prev_idx: int, prev_tail: int, t: AlignmentSpan):
                if not is_target and prev_idx != t.index:
                    for _x in range(prev_idx, t.index):
                        if prev_tail < len(sents[_x]):
                            _spans.append(sents[_x][prev_tail:])
                        prev_tail = 0
                    prev_idx = t.index
                if prev_tail != t.start:
                    _spans.append(sents[prev_idx][prev_tail : t.start])
                    prev_tail = t.start
                return prev_idx, prev_tail

            _als2idx: Dict[AlignmentSpan, int] = {}
            prev_idx: int = 0
            prev_tail: int = 0
            for t in sorted(_als):
                prev_idx, prev_tail = _pad(prev_idx, prev_tail, t)
                _als2idx[t] = len(_spans)
                if is_target:
                    _spans.append(sents[0][t.start : t.end])
                else:
                    _spans.append(sents[t.index][t.start : t.end])
                prev_tail = t.end

            for _x in range(prev_idx, len(sents)):
                _spans.append(sents[_x][prev_tail:])
                prev_tail = 0

            assert "".join(_spans) == "".join(sents), ("".join(_spans), "".join(sents))
            return _spans, _als2idx

        for target_idx, alignments in enumerate(self.alignments_list):
            _targets: List[AlignmentSpan] = []
            _origins: List[AlignmentSpan] = []
            _origin_als2tmpals: Dict[Tuple[bool, AlignmentSpan], AlignmentSpan] = {}
            for al in alignments:
                for t in al.targets:
                    _targets.append(t)
                for _in_context, o in zip(al.origins_in_context, al.origins):
                    if _in_context:
                        _new_index = o.index - len(self.context) + limit_context
                        if _new_index < 0:
                            continue
                    else:
                        _new_index = o.index + limit_context
                    _tmp_als = AlignmentSpan(start=o.start, end=o.end, index=_new_index)
                    _origins.append(_tmp_als)
                    _origin_als2tmpals[(_in_context, o)] = _tmp_als

            origin_spans, origin_als2idx = _convert(
                _origins, [c.text for c in self.context[-limit_context:]] + self.sources, False
            )
            target_spans, target_als2idx = _convert(_targets, [self.targets[target_idx]], True)

            align: List[Tuple[int, int]] = []
            import itertools

            for _my_alignment in alignments:
                for pair in itertools.product(
                    _my_alignment.targets, list(zip(_my_alignment.origins_in_context, _my_alignment.origins))
                ):
                    if pair[1][0] is True and pair[1][1].index < len(self.context) - limit_context:
                        continue
                    align.append(
                        (
                            origin_als2idx[_origin_als2tmpals[(pair[1][0], pair[1][1])]],
                            target_als2idx[pair[0]],
                        )
                    )

            yield AlignmentDump(
                sid=self.sid,
                origin_spans=origin_spans,
                target_spans=target_spans,
                align=sorted(align),
                purpose=self.meta["purpose"],
            )

    def show(self, limit_context: int) -> Iterator[str]:
        if self.alignments_list is None or len(self.alignments_list) == 0:
            return

        yield f"=== {self.sid}\n"
        yield f"Context\t{self.context}\n"
        yield f"Sources\t{self.sources}\n"
        yield f"Source_idx\t{self.source_index}\n"
        yield f"Targets\t{self.targets}\n"
        for alignments in self.alignments_list:
            for al in alignments:
                for alspan in al.targets:
                    yield f"TGT: {alspan}\t{alspan.get_text(self.targets)}\t"
                _srcs = []
                for is_in_context, alspan in zip(al.origins_in_context, al.origins):
                    strs: List[str] = self.sources
                    mark: str = ""
                    if is_in_context:
                        strs = [c.text for c in self.context]
                        if len(self.context) - alspan.index <= limit_context:
                            mark += "@"
                        else:
                            mark += "#"

                    _srcs.append(f"{mark}{alspan.get_text(strs)}")
                yield f'{" ".join(_srcs)}\n'
            yield "\n"

    def __lt__(self, other) -> bool:
        return self.sid < other.sid
