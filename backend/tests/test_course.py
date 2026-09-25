from app.models.course import Course


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