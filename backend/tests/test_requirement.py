from app.models.requirement import (
    AndRequirement,
    CourseRequirement,
    OrRequirement,
)


def test_course_requirement():
    requirement = CourseRequirement("ECS 36B")

    assert requirement.course_code == "ECS 36B"


def test_and_requirement():
    requirement = AndRequirement(
        requirements=(
            CourseRequirement("ECS 20"),
            CourseRequirement("ECS 36B"),
        )
    )

    assert len(requirement.requirements) == 2


def test_nested_requirement():
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

    assert len(requirement.requirements) == 2
    assert isinstance(requirement.requirements[0], OrRequirement)
    assert isinstance(requirement.requirements[1], CourseRequirement)