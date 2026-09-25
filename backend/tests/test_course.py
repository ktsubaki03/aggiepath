from app.models.course import Course

from app.models.course import Course
from app.models.requirement import (
    AndRequirement,
    CourseRequirement,
    OrRequirement,
)

def test_create_course():
    course = Course(
        code="ECS 36C",
        name="Data Structures",
        units=4
    )

    assert course.code == "ECS 36C"
    assert course.name == "Data Structures"
    assert course.units == 4
    assert course.description == ""
    assert course.prerequisites is None


def test_courses_are_equal():
    first = Course("ECS 36C", "Data Structures", 4)
    second = Course("ECS 36C", "Data Structures", 4)

    assert first == second

def test_course_with_prerequisites():
    prerequisites = AndRequirement(
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

    course = Course(
        code="TEST 100",
        name="Test Course",
        units=4,
        prerequisites=prerequisites,
    )

    assert course.prerequisites == prerequisites
    assert isinstance(course.prerequisites, AndRequirement)