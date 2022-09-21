#!/usr/bin/env python3
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, validator

from asdc.schema.id import DocID


class VanillaUtterance(BaseModel):
    name: str
    text: str

    @validator("name")
    def validate_name(cls, v):
        if v not in {"user", "agent", "answer", "question"}:
            raise ValueError("invalid name")
        return v


class VanillaUtterances(BaseModel):
    docid: DocID
    purpose: Literal["test", "train", "dev"]
    meta: Dict[str, Any]
    utterances: List[VanillaUtterance]
