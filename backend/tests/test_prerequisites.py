import pytest

from app.models.requirement import (
    AndRequirement,
    OrRequirement,
    CourseRequirement,
    Requirement,
)
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

@pytest.mark.parametrize("completed", [{"ECS 36B"}, {"ECS 20"}, set()])
def test_evaluate_course_requirement(completed):
    requirement = CourseRequirement("ECS 36B")
    result = evaluate(requirement, completed)

    assert result.satisfied == ("ECS 36B" in completed)
    assert result.satisfied == is_satisfied(requirement, completed)
    if result.satisfied:
        assert result.missing is None
    else:
        assert result.missing is requirement


ECS20 = CourseRequirement("ECS 20")
MAT108 = CourseRequirement("MAT 108")
ECS36B = CourseRequirement("ECS 36B")
ECS36C = CourseRequirement("ECS 36C")
CHOICE = OrRequirement((ECS20, MAT108))
NESTED = AndRequirement((CHOICE, ECS36B))
ALTERNATIVE_PATHS = OrRequirement((
    AndRequirement((ECS20, ECS36B)),
    AndRequirement((MAT108, ECS36C)),
))


@pytest.mark.parametrize(
    "requirement, completed, expected_missing",
    [
        (AndRequirement((ECS20, ECS36B)), {"ECS 20", "ECS 36B"}, None),
        (AndRequirement((ECS20, ECS36B)), set(), AndRequirement((ECS20, ECS36B))),
        (AndRequirement((ECS20, ECS36B)), {"ECS 20"}, AndRequirement((ECS36B,))),
        (AndRequirement((ECS20, ECS36B)), {"ECS 36B"}, AndRequirement((ECS20,))),
        (CHOICE, {"ECS 20"}, None),
        (CHOICE, {"MAT 108"}, None),
        (CHOICE, {"ECS 20", "MAT 108"}, None),
        (CHOICE, {"ECS 36B"}, CHOICE),
        (NESTED, {"ECS 20", "ECS 36B"}, None),
        (NESTED, {"MAT 108", "ECS 36B"}, None),
        (NESTED, set(), NESTED),
        (NESTED, {"ECS 36B"}, AndRequirement((CHOICE,))),
        (NESTED, {"MAT 108"}, AndRequirement((ECS36B,))),
        (NESTED, {"ECS 20"}, AndRequirement((ECS36B,))),
        (ALTERNATIVE_PATHS, {"ECS 20", "ECS 36B"}, None),
        (ALTERNATIVE_PATHS, {"MAT 108", "ECS 36C"}, None),
        (ALTERNATIVE_PATHS, set(), ALTERNATIVE_PATHS),
        (
            ALTERNATIVE_PATHS,
            {"ECS 20", "MAT 108"},
            OrRequirement((AndRequirement((ECS36B,)), AndRequirement((ECS36C,)))),
        ),
        (
            AndRequirement((ALTERNATIVE_PATHS, ECS20)),
            {"ECS 20", "MAT 108"},
            AndRequirement((OrRequirement((
                AndRequirement((ECS36B,)), AndRequirement((ECS36C,)),
            )),)),
        ),
        (AndRequirement(()), set(), None),
        (OrRequirement(()), set(), OrRequirement(())),
        (AndRequirement((OrRequirement(()), ECS20)), {"ECS 20"},
         AndRequirement((OrRequirement(()),))),
        (OrRequirement((AndRequirement(()), ECS20)), set(), None),
        (AndRequirement((ECS20,)), set(), AndRequirement((ECS20,))),
        (OrRequirement((ECS20,)), set(), OrRequirement((ECS20,))),
    ],
)
def test_evaluate_requirement_tree(requirement, completed, expected_missing):
    original_completed = completed.copy()
    original_children = requirement.requirements

    result = evaluate(requirement, completed)

    assert result.satisfied == (expected_missing is None)
    assert result.missing == expected_missing
    assert result.satisfied == is_satisfied(requirement, completed)
    assert completed == original_completed
    assert requirement.requirements is original_children
    if result.missing is not None:
        assert not is_satisfied(result.missing, completed)


@pytest.mark.parametrize("evaluator", [evaluate, is_satisfied])
@pytest.mark.parametrize("wrapper", [
    lambda r: r, lambda r: AndRequirement((r,)), lambda r: OrRequirement((r,)),
])
def test_unsupported_requirement_type(evaluator, wrapper):
    with pytest.raises(TypeError, match="Unsupported requirement type"):
        evaluator(wrapper(Requirement()), set())
