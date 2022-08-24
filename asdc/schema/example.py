#!/usr/bin/env python3

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, validator

from asdc.schema.id import SID

METACHAR_SENTENCE_BOUNDARY: str = "\u2502"
METACHAR_LINE_BREAK: str = "\u2581"
METAKEY_INCORRECT: str = "incorrect"


class SimpleUtterance(BaseModel):
    speaker: Literal["user", "agent"]
    text: str


class Example(BaseModel):
    sid: SID
    sources: List[str] = Field(min_items=1)  # List of sentences
    targets: List[str]
    context: List[SimpleUtterance]
    purpose: Literal["test", "train", "dev"]
    meta: Dict[str, Any]

    @validator("targets")
    def validate_targets(cls, v):
        for t in v:
            if "<none>" in t:
                raise ValueError("<none> should not be in targets")
        return v

    def __lt__(self, other) -> bool:
        return self.sid < other.sid
