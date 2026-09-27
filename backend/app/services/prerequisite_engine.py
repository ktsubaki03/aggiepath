from dataclasses import dataclass

from app.models.requirement import (
    AndRequirement,
    CourseRequirement,
    OrRequirement,
    Requirement,
)


@dataclass(frozen=True)
class EvaluationResult:
    satisfied: bool
    missing: Requirement | None = None


def evaluate(
    requirement: Requirement,
    completed_courses: set[str],
) -> EvaluationResult:
    """Return satisfaction and the remaining prerequisite tree without flattening it."""
    if isinstance(requirement, CourseRequirement):
        if requirement.course_code in completed_courses:
            return EvaluationResult(satisfied=True)

        return EvaluationResult(
            satisfied=False,
            missing=requirement,
        )

    if isinstance(requirement, AndRequirement):
        missing = []
        for child in requirement.requirements:
            result = evaluate(child, completed_courses)
            if result.missing is not None:
                missing.append(result.missing)

        if not missing:
            return EvaluationResult(satisfied=True)
        return EvaluationResult(
            satisfied=False,
            missing=AndRequirement(tuple(missing)),
        )

    if isinstance(requirement, OrRequirement):
        missing = []
        for child in requirement.requirements:
            result = evaluate(child, completed_courses)
            if result.satisfied:
                return EvaluationResult(satisfied=True)
            if result.missing is not None:
                missing.append(result.missing)

        return EvaluationResult(
            satisfied=False,
            missing=OrRequirement(tuple(missing)),
        )

    raise TypeError(f"Unsupported requirement type: {type(requirement)}")


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
