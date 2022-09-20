#!/usr/bin/env python3


from typing import Any, Dict, List

from pydantic import BaseModel, validator

from asdc.schema.id import DocID


class Meta(BaseModel):
    id: DocID
    memo: str = ""
    data: Dict[str, Any] = {}


class VanillaUtterance(BaseModel):
    name: str
    text: str

    @validator("name")
    def validate_name(cls, v):
        if v not in {"user", "agent", "answer", "question"}:
            raise ValueError("invalid name")
        return v


class VanillaUtterances(BaseModel):
    meta: Meta
    utterances: List[VanillaUtterance]
