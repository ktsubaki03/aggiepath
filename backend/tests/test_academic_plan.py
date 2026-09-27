from dataclasses import FrozenInstanceError

import pytest

from app.models.academic_plan import AcademicPlan, PlannedCourse, Quarter, Term


def test_planned_course_stores_code():
    assert PlannedCourse("ECS 36B").course_code == "ECS 36B"


@pytest.mark.parametrize("code", ["", " ", "\t\n", None, 36])
def test_planned_course_rejects_invalid_codes(code):
    with pytest.raises(ValueError, match="course_code must be a non-empty string"):
        PlannedCourse(code)


def test_quarter_stores_fields_and_courses():
    courses = (PlannedCourse("ECS 36B"), PlannedCourse("ECS 20"))
    quarter = Quarter(Term.FALL, 2026, courses)
    assert quarter.term is Term.FALL
    assert quarter.year == 2026
    assert quarter.courses == courses


def test_quarter_defaults_to_no_courses():
    assert Quarter(Term.WINTER, 2027).courses == ()


@pytest.mark.parametrize("year", [0, -1, -2026, 2026.5, "2026", None, True, False])
def test_quarter_rejects_invalid_years(year):
    with pytest.raises(ValueError, match="year must be a positive integer"):
        Quarter(Term.FALL, year)


def test_quarter_accepts_positive_year():
    assert Quarter(Term.WINTER, 1).year == 1


def test_quarter_rejects_duplicate_codes():
    with pytest.raises(ValueError, match="duplicate course code.*ECS 36B"):
        Quarter(Term.FALL, 2026, (PlannedCourse("ECS 36B"), PlannedCourse("ECS 36B")))


def test_chronological_order_within_year():
    quarters = [Quarter(term, 2026) for term in
                (Term.FALL, Term.SPRING, Term.WINTER, Term.SUMMER)]
    ordered = sorted(quarters, key=lambda quarter: quarter.sort_key)
    assert [quarter.term for quarter in ordered] == [
        Term.WINTER, Term.SPRING, Term.SUMMER, Term.FALL,
    ]
    assert [quarter.sort_key for quarter in ordered] == [
        (2026, 1), (2026, 2), (2026, 3), (2026, 4),
    ]


def test_chronological_order_across_years():
    quarters = [Quarter(Term.WINTER, 2027), Quarter(Term.FALL, 2025),
                Quarter(Term.FALL, 2026), Quarter(Term.WINTER, 2026)]
    assert sorted(quarters, key=lambda quarter: quarter.sort_key) == [
        quarters[1], quarters[3], quarters[2], quarters[0],
    ]


def test_plan_stores_completed_courses_and_defaults_to_no_quarters():
    completed = frozenset(("ECS 20", "ECS 36A", "ECS 20"))
    plan = AcademicPlan(completed)
    assert isinstance(plan.completed_courses, frozenset)
    assert plan.completed_courses == frozenset({"ECS 20", "ECS 36A"})
    assert plan.quarters == ()


def test_plan_preserves_supplied_quarter_order():
    quarters = (Quarter(Term.FALL, 2027), Quarter(Term.WINTER, 2027))
    assert AcademicPlan(frozenset(), quarters).quarters == quarters


@pytest.mark.parametrize("code", ["", " ", "\t\n", None, 20])
def test_plan_rejects_invalid_completed_codes(code):
    with pytest.raises(ValueError, match="completed course codes must be non-empty strings"):
        AcademicPlan(frozenset({"ECS 20", code}))


def test_same_course_allowed_in_different_quarters_and_completed_courses():
    course = PlannedCourse("ECS 36B")
    quarters = (Quarter(Term.FALL, 2026, (course,)), Quarter(Term.WINTER, 2027, (course,)))
    plan = AcademicPlan(frozenset({"ECS 36B"}), quarters)
    assert plan.quarters == quarters


def test_multi_quarter_plan():
    plan = AcademicPlan(
        completed_courses=frozenset({"ECS 36A", "MAT 21A"}),
        quarters=(
            Quarter(Term.FALL, 2026, (PlannedCourse("ECS 20"), PlannedCourse("ECS 36B"))),
            Quarter(Term.WINTER, 2027, (PlannedCourse("ECS 36C"), PlannedCourse("MAT 21B"))),
            Quarter(Term.SPRING, 2027, (PlannedCourse("ECS 150"),)),
        ),
    )
    assert len(plan.quarters) == 3
    assert sum(len(quarter.courses) for quarter in plan.quarters) == 5
    assert tuple(sorted(plan.quarters, key=lambda quarter: quarter.sort_key)) == plan.quarters


@pytest.mark.parametrize("instance, field, value", [
    (PlannedCourse("ECS 20"), "course_code", "MAT 108"),
    (Quarter(Term.FALL, 2026), "year", 2027),
    (AcademicPlan(frozenset()), "quarters", (Quarter(Term.FALL, 2026),)),
])
def test_models_are_frozen(instance, field, value):
    with pytest.raises(FrozenInstanceError):
        setattr(instance, field, value)


@pytest.mark.parametrize("factory, message", [
    (lambda: Quarter("Fall", 2026), "term must be a Term"),
    (lambda: Quarter(Term.FALL, 2026, []), "courses must be a tuple"),
    (lambda: Quarter(Term.FALL, 2026, ("ECS 20",)), "courses must contain PlannedCourse"),
    (lambda: AcademicPlan(set()), "completed_courses must be a frozenset"),
    (lambda: AcademicPlan(frozenset(), []), "quarters must be a tuple"),
    (lambda: AcademicPlan(frozenset(), ("Fall",)), "quarters must contain Quarter"),
])
def test_models_reject_wrong_container_and_member_types(factory, message):
    with pytest.raises(TypeError, match=message):
        factory()
