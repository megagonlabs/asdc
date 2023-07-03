#!/usr/bin/env python3
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, FieldValidationInfo, field_validator, model_validator

from asdc.schema.id import SID, DocID

METACHAR_SENTENCE_BOUNDARY: str = "\u2502"
METACHAR_LINE_BREAK: str = "\u2581"


class VanillaUtterance(BaseModel):
    name: Literal["user", "agent"]
    text: str


class VanillaUtterances(BaseModel):
    docid: DocID
    purpose: Literal["test", "train", "dev"]
    meta: dict[str, Any]
    utterances: list[VanillaUtterance]


INCORRECT_TYPES = Literal[
    "lack",
    "limited",
    "untruth",
    "non_fluent",
    "incorrect_none",
]


class Example(BaseModel):
    sid: SID
    sources: list[str] = Field(min_length=1)  # List of sentences
    targets: list[str]  # SCUDs of focused_source
    context: list[VanillaUtterance]
    purpose: Literal["test", "train", "dev"]
    meta: dict[str, Any]

    correct: Optional[bool]
    example_types: Optional[list[INCORRECT_TYPES]]
    original_sid: Optional[SID]

    @property
    def focused_source(self) -> str:
        return self.sources[self.sid.sentence_num]

    @model_validator(mode="after")
    def validate_sid(self, info):
        if 0 <= self.sid.sentence_num < len(self.sources):
            return self
        raise ValueError("Invalid sentence number")

    @field_validator("targets")
    def validate_targets(cls, v: list[str], info: FieldValidationInfo):
        for t in v:
            if "<none>" in t:
                raise ValueError("<none> should not be in targets")
            if len(t.strip()) == 0:
                raise ValueError(f"Blank target should not be in targets {v}")
        return v

    def __lt__(self, other) -> bool:
        return self.sid < other.sid
