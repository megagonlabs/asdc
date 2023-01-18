#!/usr/bin/env python3
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, root_validator, validator

from asdc.schema.id import SID, DocID

METACHAR_SENTENCE_BOUNDARY: str = "\u2502"
METACHAR_LINE_BREAK: str = "\u2581"


class VanillaUtterance(BaseModel):
    name: Literal["user", "agent"]
    text: str


class VanillaUtterances(BaseModel):
    docid: DocID
    purpose: Literal["test", "train", "dev"]
    meta: Dict[str, Any]
    utterances: List[VanillaUtterance]


INCORRECT_TYPES = Literal[
    "lack",
    "limited",
    "untruth",
    "non_fluent",
    "incorrect_none",
]


class Example(BaseModel):
    sid: SID
    sources: List[str] = Field(min_items=1)  # List of sentences
    targets: List[str]  # SCUDs of focused_source
    context: List[VanillaUtterance]
    purpose: Literal["test", "train", "dev"]
    meta: Dict[str, Any]

    correct: Optional[bool]
    example_types: Optional[List[INCORRECT_TYPES]]
    original_sid: Optional[SID]

    @property
    def focused_source(self) -> str:
        return self.sources[self.sid.sentence_num]

    @root_validator
    def validate_sid(cls, values):
        if 0 <= values["sid"].sentence_num < len(values["sources"]):
            return values
        raise ValueError("Invalid sentence number")

    @validator("targets")
    def validate_targets(cls, v):
        for t in v:
            if "<none>" in t:
                raise ValueError("<none> should not be in targets")
            if len(t.strip()) == 0:
                raise ValueError(f"Blank target should not be in targets {v}")
        return v

    def __lt__(self, other) -> bool:
        return self.sid < other.sid
