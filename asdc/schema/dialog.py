#!/usr/bin/env python3
import enum
from pathlib import Path
from typing import Iterator, NewType, Union

from pydantic import BaseModel, validator

from asdc.schema.example import METACHAR_LINE_BREAK, VanillaUtterance
from asdc.schema.id import SID, DocID, UttrID


class Span(BaseModel):
    is_target: bool
    sid: SID
    start: int
    end: int

    def get_text(self, src: str, tgt: str) -> str:
        if self.is_target:
            return tgt[self.start : self.end]
        return src[self.start : self.end]

    def __lt__(self, other) -> bool:
        if self.is_target != other.is_target:
            return int(self.is_target) < int(other.is_target)
        if self.sid != other.sid:
            return self.sid < other.sid
        if self.start != other.start:
            return self.start < other.start
        return self.end < other.end


class GroupType(enum.Enum):
    ERROR = "ERROR"
    INSIDE = "INSIDE"
    BOTHSIDE = "BOTHSIDE"
    OUTSIDE = "OUTSIDE"
    EXOPHORA = "EXOPHORA"


class SpanGroup(BaseModel):
    group_type: GroupType
    spans: list[Span]

    def __lt__(self, other) -> bool:
        if self.group_type != other.group_type:
            order = [GroupType.ERROR, GroupType.INSIDE, GroupType.BOTHSIDE, GroupType.OUTSIDE, GroupType.EXOPHORA]
            return order.index(self.group_type) < order.index(other.group_type)
        return sorted(self.spans)[0] < sorted(other.spans)[0]

    @property
    def has_source(self) -> bool:
        for span in self.spans:
            if not span.is_target:
                return True
        return False

    @property
    def has_target(self) -> bool:
        for span in self.spans:
            if span.is_target:
                return True
        return False


class AlignmentSpan(BaseModel):
    index: int
    start: int
    end: int

    def get_text(self, strs: list[str]) -> str:
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


class Scud(BaseModel):
    """
    発話文の1つのSCUDを表現するクラス

    sid:
        文ID

    idx:
        番号

    text:
        発話文

    scud:
        SCUD

    queries:
        対応する要件

    memo:
        アノテーションメモ

    groups:
        発話文とSCUDの対応関係
    """

    sid: SID
    idx: int
    text: str
    scud: str
    queries: list[str]
    memo: str
    groups: list[SpanGroup]

    @property
    def id(self) -> str:
        return f"scud/{self.sid.id}/{self.idx}"

    @staticmethod
    def id2sid(id: str) -> SID:
        assert id.startswith("scud/")
        return SID(id=id[len("scud/") : id.rindex("/")])

    @staticmethod
    def id2idx(id: str) -> int:
        assert id.startswith("scud/")
        return int(id[id.rindex("/") + 1 :])

    def __lt__(self, other) -> bool:
        if self.sid != other.sid:
            return self.sid < other.sid
        return self.idx < other.idx

    @validator("groups")
    def validate_alignment(cls, v):
        # check span duplication
        covered: set[tuple[bool, SID, int]] = set()
        for sg in v:
            span: Span
            for span in sg.spans:
                for idx in range(span.start, span.end):
                    p = (span.is_target, span.sid, idx)
                    if p in covered:
                        raise ValueError(f"Duplication {p}")
                    covered.add(p)
        return v


Sid2Scuds = NewType("Sid2Scuds", dict[SID, list[Scud]])


def open_scud_file(ifname: Path) -> Sid2Scuds:
    assert ifname.is_dir()

    sid2scuds: Sid2Scuds = Sid2Scuds({})
    for _in in ifname.iterdir():
        with _in.open() as inf:
            for line in inf:
                scud = Scud.parse_raw(line)
                if scud.sid not in sid2scuds:
                    sid2scuds[scud.sid] = []
                sid2scuds[scud.sid].append(scud)
    return sid2scuds


Docid2Scuds = NewType("Docid2Scuds", dict[DocID, list[Scud]])


def open_scud_file_by_docid(ifname: Path) -> Docid2Scuds:
    docid2scuds: Docid2Scuds = Docid2Scuds({})
    for _i in ifname.iterdir():
        with _i.open() as inf:
            for line in inf:
                scud = Scud.parse_raw(line)
                docid = scud.sid.docid
                if docid not in docid2scuds:
                    docid2scuds[docid] = []
                docid2scuds[docid].append(scud)
    return docid2scuds


class Utterance(BaseModel):
    """
    発話を表現するクラス

    id:
        発話ID

    name:
        発話者名

    text:
        発話文

    text_sbs:
        文境界文字インデックス

    time:
        第1発話の時刻を``0``として，それからの経過秒数
    """

    id: UttrID
    name: str
    text: str
    text_sbs: list[int]
    time: float

    def yield_sentence(self, meta: bool = False) -> Iterator[str]:
        last = 0
        for idx in self.text_sbs:
            if meta:
                yield self.text[last:idx].replace("\n", METACHAR_LINE_BREAK)
            else:
                yield self.text[last:idx]
            last = idx


class Meta(BaseModel):
    id: DocID
    area: str
    dialog_month: int
    dialog_day: int
    travel_month: int
    travel_day: Union[int, str]
    travel_duration: int
    num_adult: int
    num_child: int
    conditions: list[str]
    memo: str
    purpose: str

    @validator("purpose")
    def validate_purpose(cls, v):
        if v not in ["test", "train", "dev"]:
            raise ValueError("invalid propose")
        return v


class Utterances(BaseModel):
    meta: Meta
    utterances: list[Utterance]

    def get(self, *, sid: SID) -> str:
        uttr_idx: int = sid.uttrid.num
        snum: int = sid.sentence_num

        u = self.utterances[uttr_idx]
        for lid, sent in enumerate(u.yield_sentence(meta=True)):
            if lid == snum:
                return sent
        raise KeyError

    def get_contexts(self, sid: SID, same_uttr: bool, by_uttr: bool) -> list[VanillaUtterance]:
        uttr_id = sid.uttrid
        _idx = sid.sentence_num

        out: list[VanillaUtterance] = []
        for u in self.utterances:
            name: str = "agent"
            if u.name.startswith("user"):
                name = "user"

            if not same_uttr and u.id == uttr_id:
                break
            for lid, sent in enumerate(u.yield_sentence(meta=True)):
                if same_uttr and u.id == uttr_id and lid == _idx:
                    return out
                if by_uttr:
                    if lid == 0:
                        out.append(VanillaUtterance(name=name, text=""))
                    out[-1].text += sent
                else:
                    out.append(VanillaUtterance(name=name, text=sent))
        return out


class Docid2Utterances(dict):
    def __init__(self, ref: Path):
        assert ref.is_dir()
        for afile in ref.iterdir():
            uttrs = Utterances.parse_file(afile)
            self[uttrs.meta.id] = uttrs
