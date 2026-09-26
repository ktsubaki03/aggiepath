from app.models.requirement import (
    AndRequirement,
    CourseRequirement,
    OrRequirement,
    Requirement,
)

from dataclasses import dataclass

@dataclass(frozen=True)
class EvaluationResult:
    satisfied: bool
    missing_courses: tuple[str, ...] = ()

def evaluate(
    requirement: Requirement,
    completed_courses: set[str],
) -> EvaluationResult:
    if isinstance(requirement, CourseRequirement):
        if requirement.course_code in completed_courses:
            return EvaluationResult(satisfied=True)

        return EvaluationResult(
            satisfied=False,
            missing_courses=(requirement.course_code,),
        )

def is_satisfied(
    requirement: Requirement,
    completed_courses: set[str],
) -> bool:
    if isinstance(requirement, CourseRequirement):
        return requirement.course_code in completed_courses

    if isinstance(requirement, AndRequirement):
        return all(
            is_satisfied(child, completed_courses)
            for child in requirement.requirements
        )

    if isinstance(requirement, OrRequirement):
        return any(
            is_satisfied(child, completed_courses)
            for child in requirement.requirements
        )

    raise TypeError(f"Unsupported requirement type: {type(requirement)}")

