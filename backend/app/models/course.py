from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .requirement import Requirement


@dataclass(frozen=True)
class Course:
    code: str
    name: str
    units: int
    description: str = ""
    prerequisites: Requirement | None = None