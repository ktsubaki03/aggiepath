import json
from pathlib import Path

import pytest

from app.models.course import Course
from app.models.requirement import AndRequirement, CourseRequirement, OrRequirement
from app.services.course_catalog import load_course_catalog, parse_requirement
from app.services.prerequisite_engine import evaluate, is_satisfied


SAMPLE = Path(__file__).resolve().parents[1] / "app/data/courses/ecs.json"
ECS20 = CourseRequirement("ECS 20")
ECS36B = CourseRequirement("ECS 36B")
CHOICE = OrRequirement((ECS20, CourseRequirement("MAT 108")))
NESTED = AndRequirement((CHOICE, ECS36B))


@pytest.fixture
def write_catalog(tmp_path):
    def write(data):
        path = tmp_path / "catalog.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path
    return write


@pytest.mark.parametrize("number, expected", [
    (1, None),
    (2, ECS20),
    (3, AndRequirement((ECS20, ECS36B))),
    (4, CHOICE),
    (5, NESTED),
])
def test_sample_course_structures(number, expected):
    catalog = load_course_catalog(SAMPLE)
    assert len(catalog) == 5
    course = catalog[f"ECS SAMPLE {number}"]
    assert isinstance(course, Course)
    assert course.prerequisites == expected
    assert course.code == f"ECS SAMPLE {number}"
    assert course.units == 4
    assert course.name.startswith("Sample:")


def test_basic_fields_defaults_and_retrieval(write_catalog):
    path = write_catalog([
        {"code": "TEST 1", "name": "Example", "units": 0},
        {"code": "TEST 2", "name": "Example 2", "units": 4,
         "description": "Sample description", "prerequisites": None},
    ])
    catalog = load_course_catalog(str(path))
    assert catalog["TEST 1"] == Course("TEST 1", "Example", 0)
    assert catalog["TEST 2"] == Course("TEST 2", "Example 2", 4, "Sample description")
    assert catalog.get("UNKNOWN") is None
    with pytest.raises(KeyError):
        catalog["UNKNOWN"]


@pytest.mark.parametrize("completed, missing", [
    ({"MAT 108", "ECS 36B"}, None),
    ({"ECS 20", "ECS 36B"}, None),
    ({"ECS 36B"}, AndRequirement((CHOICE,))),
    ({"ECS 20"}, AndRequirement((ECS36B,))),
    (set(), NESTED),
])
def test_json_to_evaluation(completed, missing):
    course = load_course_catalog(SAMPLE)["ECS SAMPLE 5"]
    result = evaluate(course.prerequisites, completed)
    assert result.satisfied == (missing is None)
    assert result.missing == missing
    assert is_satisfied(course.prerequisites, completed) == result.satisfied


def test_deeper_nesting(write_catalog):
    node = {"type": "course", "course_code": "EXTERNAL 1"}
    expected = CourseRequirement("EXTERNAL 1")
    for kind, model in [("or", OrRequirement), ("and", AndRequirement)] * 4:
        node = {"type": kind, "requirements": [node]}
        expected = model((expected,))
    path = write_catalog([
        {"code": "TEST", "name": "Nested", "units": 1, "prerequisites": node},
    ])
    requirement = load_course_catalog(path)["TEST"].prerequisites
    assert requirement == expected
    assert is_satisfied(requirement, {"EXTERNAL 1"})
    assert not is_satisfied(requirement, set())


@pytest.mark.parametrize("node, message", [
    (False, "expected a requirement object"),
    ([], "expected a requirement object"),
    ("ECS 20", "expected a requirement object"),
    ({}, "unsupported requirement type"),
    ({"type": "xor"}, "unsupported requirement type"),
    ({"type": []}, "unsupported requirement type"),
    ({"type": "course"}, "missing fields"),
    ({"type": "course", "course_code": ""}, "non-empty string"),
    ({"type": "course", "course_code": 20}, "non-empty string"),
    ({"type": "course", "course_code": "ECS 20", "extra": 1}, "unknown fields"),
    ({"type": "and"}, "missing fields"),
    ({"type": "or", "requirements": None}, "expected an array"),
    ({"type": "and", "requirements": {}}, "expected an array"),
    ({"type": "and", "requirements": [None]}, "requirements\\[0\\]"),
    ({"type": "or", "requirements": [{"type": "bad"}]}, "requirements\\[0\\]"),
    ({"type": "and", "requirements": [], "course_code": "X"}, "unknown fields"),
])
def test_invalid_prerequisites_are_rejected(write_catalog, node, message):
    path = write_catalog([
        {"code": "TEST", "name": "Example", "units": 4, "prerequisites": node},
    ])
    with pytest.raises(ValueError, match=message) as error:
        load_course_catalog(path)
    assert "courses[0].prerequisites" in str(error.value)


@pytest.mark.parametrize("kind, expected, satisfied", [
    ("and", AndRequirement(()), True),
    ("or", OrRequirement(()), False),
])
def test_empty_groups_match_evaluator(kind, expected, satisfied):
    requirement = parse_requirement({"type": kind, "requirements": []})
    assert requirement == expected
    assert is_satisfied(requirement, set()) is satisfied


@pytest.mark.parametrize("changes, message", [
    ({"code": " "}, "code: expected a non-empty string"),
    ({"name": None}, "name: expected a non-empty string"),
    ({"units": True}, "units: expected a non-negative integer"),
    ({"units": -1}, "units: expected a non-negative integer"),
    ({"units": 4.5}, "units: expected a non-negative integer"),
    ({"units": "4"}, "units: expected a non-negative integer"),
    ({"description": None}, "description: expected a string"),
    ({"prerequisite": None}, "unknown fields"),
])
def test_invalid_course_fields(write_catalog, changes, message):
    record = {"code": "TEST", "name": "Example", "units": 4}
    record.update(changes)
    with pytest.raises(ValueError, match=message):
        load_course_catalog(write_catalog([record]))


@pytest.mark.parametrize("data, message", [
    ({}, "catalog must be an array"),
    (None, "catalog must be an array"),
    ([None], "expected an object"),
    ([{}], "missing fields"),
])
def test_invalid_catalog(write_catalog, data, message):
    with pytest.raises(ValueError, match=message):
        load_course_catalog(write_catalog(data))


def test_duplicate_codes(write_catalog):
    record = {"code": "TEST", "name": "Example", "units": 4}
    with pytest.raises(ValueError, match="duplicate course code 'TEST'"):
        load_course_catalog(write_catalog([record, record]))


def test_empty_catalog(write_catalog):
    assert load_course_catalog(write_catalog([])) == {}


def test_invalid_json(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("[{", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_course_catalog(path)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_course_catalog(tmp_path / "missing.json")
