"""Deserialize JSON catalogs into domain models, without evaluating prerequisites."""

import json
from pathlib import Path

from app.models.course import Course
from app.models.requirement import (
    AndRequirement,
    CourseRequirement,
    OrRequirement,
    Requirement,
)


def _fields(
    data: object, required: set[str], optional: set[str], context: str,
) -> dict:
    if not isinstance(data, dict):
        raise ValueError(f"{context}: expected an object")
    missing = required - data.keys()
    unknown = data.keys() - required - optional
    if missing or unknown:
        raise ValueError(
            f"{context}: missing fields {sorted(missing)}; "
            f"unknown fields {sorted(unknown)}"
        )
    return data


def _nonempty_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: expected a non-empty string")
    return value


def parse_requirement(data: object, *, context: str = "prerequisites") -> Requirement:
    """Parse a tagged requirement tree. Null is allowed only at the course root."""
    if not isinstance(data, dict):
        raise ValueError(f"{context}: expected a requirement object")
    kind = data.get("type")
    if kind == "course":
        node = _fields(data, {"type", "course_code"}, set(), context)
        return CourseRequirement(
            _nonempty_string(node["course_code"], f"{context}.course_code")
        )
    if kind in ("and", "or"):
        node = _fields(data, {"type", "requirements"}, set(), context)
        children = node["requirements"]
        if not isinstance(children, list):
            raise ValueError(f"{context}.requirements: expected an array")
        requirements = tuple(
            parse_requirement(child, context=f"{context}.requirements[{index}]")
            for index, child in enumerate(children)
        )
        return AndRequirement(requirements) if kind == "and" else OrRequirement(requirements)
    raise ValueError(f"{context}: unsupported requirement type {kind!r}")


def load_course_catalog(path: str | Path) -> dict[str, Course]:
    """Load one JSON array, indexed by exact course code; reject duplicate codes."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{path}: invalid JSON: {error}") from error
    if not isinstance(data, list):
        raise ValueError(f"{path}: catalog must be an array of courses")

    catalog: dict[str, Course] = {}
    for index, record in enumerate(data):
        context = f"{path}: courses[{index}]"
        fields = _fields(
            record, {"code", "name", "units"}, {"description", "prerequisites"}, context,
        )
        code = _nonempty_string(fields["code"], f"{context}.code")
        name = _nonempty_string(fields["name"], f"{context}.name")
        units = fields["units"]
        if type(units) is not int or units < 0:
            raise ValueError(f"{context}.units: expected a non-negative integer")
        description = fields.get("description", "")
        if not isinstance(description, str):
            raise ValueError(f"{context}.description: expected a string")
        prerequisites = fields.get("prerequisites")
        requirement = (
            None if prerequisites is None else
            parse_requirement(prerequisites, context=f"{context}.prerequisites")
        )
        if code in catalog:
            raise ValueError(f"{context}: duplicate course code {code!r}")
        catalog[code] = Course(code, name, units, description, requirement)
    return catalog
