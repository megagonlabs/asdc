#!/usr/bin/env python3
from typing import Any, Dict, List, Literal

from pydantic import BaseModel

from asdc.schema.id import DocID


class VanillaUtterance(BaseModel):
    name: Literal["user", "agent"]
    text: str


class VanillaUtterances(BaseModel):
    docid: DocID
    purpose: Literal["test", "train", "dev"]
    meta: Dict[str, Any]
    utterances: List[VanillaUtterance]
