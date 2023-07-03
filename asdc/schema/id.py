#!/usr/bin/env python3


from pydantic.v1 import BaseModel, validator


class DocID(BaseModel):
    id: str

    @validator("id")
    def id_include_period(cls, v):
        if "." not in v:
            raise ValueError("must contain a period")
        return v

    @property
    def prefix(self) -> str:
        return self.id[: self.id.rindex(".")]

    @property
    def doc_num_str(self) -> str:
        return self.id[self.id.rindex(".") + 1 :]

    @property
    def doc_num(self) -> int:
        return int(self.id[self.id.rindex(".") + 1 :])

    def __lt__(self, other) -> bool:
        assert self.prefix == other.prefix, (self.prefix, other.prefix)
        return self.doc_num < other.doc_num

    def __hash__(self):
        return hash(self.id)


class UttrID(BaseModel):
    id: str

    @validator("id")
    def id_include_period(cls, v):
        if "." not in v:
            raise ValueError("must contain a period")
        return v

    @property
    def docid(self) -> DocID:
        return DocID(id=self.id[: self.id.rindex(".")])

    @property
    def num(self) -> int:
        return int(self.id.split(".")[-1])

    def get_sid(self, idx: int) -> "SID":
        return SID(id=f"{self.id}-{idx}")

    def __lt__(self, other) -> bool:
        if self.docid != other.docid:
            return self.docid < other.docid
        return self.num < other.num

    def __sub__(self, other) -> int:
        return self.num - other.num

    def __hash__(self):
        return hash(self.id)


class SID(BaseModel):
    id: str

    @validator("id")
    def id_include_period(cls, v):
        if "." not in v:
            raise ValueError("must contain a period")
        elif "-" not in v:
            raise ValueError("must contain a hyphen")
        elif v.startswith("id='"):
            raise ValueError("invalid assignment")
        return v

    @property
    def docid(self) -> DocID:
        return DocID(id=self.id[: self.id.rindex(".")])

    @property
    def uttrid(self) -> UttrID:
        return UttrID(id=self.id[: self.id.rindex("-")])

    @property
    def sentence_num(self) -> int:
        return int(self.id[self.id.rindex("-") + 1 :])

    def __lt__(self, other) -> bool:
        if self.docid != other.docid:
            return self.docid < other.docid
        if self.uttrid.num != other.uttrid.num:
            return self.uttrid.num < other.uttrid.num
        return self.sentence_num < other.sentence_num

    def __sub__(self, other) -> int:
        assert self.docid == other.docid
        assert self.uttrid == other.uttrid
        return self.sentence_num - other.sentence_num

    def __hash__(self):
        return hash(self.id)
