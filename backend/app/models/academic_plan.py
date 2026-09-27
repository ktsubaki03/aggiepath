"""Immutable academic-plan data; scheduling and prerequisite checks live elsewhere."""

from dataclasses import dataclass
from enum import Enum


class Term(Enum):
    """Explicit chronological order within a calendar year."""

    WINTER = 1
    SPRING = 2
    SUMMER = 3
    FALL = 4


@dataclass(frozen=True)
class PlannedCourse:
    course_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.course_code, str) or not self.course_code.strip():
            raise ValueError("course_code must be a non-empty string")


@dataclass(frozen=True)
class Quarter:
    term: Term
    year: int
    courses: tuple[PlannedCourse, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.term, Term):
            raise TypeError("term must be a Term")
        if type(self.year) is not int or self.year <= 0:
            raise ValueError("year must be a positive integer")
        if not isinstance(self.courses, tuple):
            raise TypeError("courses must be a tuple of PlannedCourse objects")
        codes: set[str] = set()
        for course in self.courses:
            if not isinstance(course, PlannedCourse):
                raise TypeError("courses must contain PlannedCourse objects")
            if course.course_code in codes:
                raise ValueError(f"duplicate course code in quarter: {course.course_code!r}")
            codes.add(course.course_code)

    @property
    def sort_key(self) -> tuple[int, int]:
        return (self.year, self.term.value)


@dataclass(frozen=True)
class AcademicPlan:
    completed_courses: frozenset[str]
    quarters: tuple[Quarter, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.completed_courses, frozenset):
            raise TypeError("completed_courses must be a frozenset of course codes")
        for code in self.completed_courses:
            if not isinstance(code, str) or not code.strip():
                raise ValueError("completed course codes must be non-empty strings")
        if not isinstance(self.quarters, tuple):
            raise TypeError("quarters must be a tuple of Quarter objects")
        if any(not isinstance(quarter, Quarter) for quarter in self.quarters):
            raise TypeError("quarters must contain Quarter objects")
