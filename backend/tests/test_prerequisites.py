from app.models.requirement import (
    AndRequirement,
    OrRequirement,
    CourseRequirement,
)
from app.services.prerequisite_engine import is_satisfied

from app.services.prerequisite_engine import evaluate, is_satisfied

def test_course_requirement_satisfied():
    requirement = CourseRequirement("ECS 36B")

    completed_courses = {
        "ECS 20",
        "ECS 36A",
        "ECS 36B",
    }

    assert is_satisfied(requirement, completed_courses)


def test_course_requirement_not_satisfied():
    requirement = CourseRequirement("ECS 36B")

    completed_courses = {
        "ECS 20",
        "ECS 36A",
    }

    assert not is_satisfied(requirement, completed_courses)

def test_and_requirement_satisfied():
    requirement = AndRequirement(
        requirements=(
            CourseRequirement("ECS 20"),
            CourseRequirement("ECS 36B"),
        )
    )

    completed_courses = {
        "ECS 20",
        "ECS 36B",
    }

    assert is_satisfied(requirement, completed_courses)


def test_and_requirement_not_satisfied():
    requirement = AndRequirement(
        requirements=(
            CourseRequirement("ECS 20"),
            CourseRequirement("ECS 36B"),
        )
    )

    completed_courses = {
        "ECS 20",
    }

    assert not is_satisfied(requirement, completed_courses)

def test_or_requirement_satisfied():
    requirement = OrRequirement(
        requirements=(
            CourseRequirement("ECS 20"),
            CourseRequirement("MAT 108"),
        )
    )

    completed_courses = {
        "ECS 20",
    }

    assert is_satisfied(requirement, completed_courses)


def test_or_requirement_not_satisfied():
    requirement = OrRequirement(
        requirements=(
            CourseRequirement("ECS 20"),
            CourseRequirement("MAT 108"),
        )
    )

    completed_courses = {
        "ECS 36B",
    }

    assert not is_satisfied(requirement, completed_courses)

def test_nested_requirement_satisfied():
    requirement = AndRequirement(
        requirements=(
            OrRequirement(
                requirements=(
                    CourseRequirement("ECS 20"),
                    CourseRequirement("MAT 108"),
                )
            ),
            CourseRequirement("ECS 36B"),
        )
    )

    completed_courses = {
        "MAT 108",
        "ECS 36B",
    }

    assert is_satisfied(requirement, completed_courses)

def test_evaluate_course_requirement_satisfied():
    requirement = CourseRequirement("ECS 36B")

    result = evaluate(
        requirement,
        {"ECS 36B"},
    )

    assert result.satisfied
    assert result.missing_courses == ()

def test_evaluate_course_requirement_satisfied():
    requirement = CourseRequirement("ECS 36B")

    result = evaluate(
        requirement,
        {"ECS 36B"},
    )

    assert result.satisfied
    assert result.missing_courses == ()

def test_evaluate_course_requirement_missing():
    requirement = CourseRequirement("ECS 36B")

    result = evaluate(
        requirement,
        {"ECS 20"},
    )

    assert not result.satisfied
    assert result.missing_courses == ("ECS 36B",)

