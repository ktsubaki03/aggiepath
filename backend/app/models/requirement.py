from __future__ import annotations

from dataclasses import dataclass
from abc import ABC


class Requirement(ABC):
    """Base class for all prerequisite requirements."""
    pass


@dataclass(frozen=True)
class CourseRequirement(Requirement):
    course_code: str


@dataclass(frozen=True)
class AndRequirement(Requirement):
    requirements: tuple[Requirement, ...]


@dataclass(frozen=True)
class OrRequirement(Requirement):
    requirements: tuple[Requirement, ...]