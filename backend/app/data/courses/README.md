# Sample course catalog

`ecs.json` contains synthetic architecture/test examples, not official UC Davis
courses or verified prerequisite information. Names, units, and prerequisite
relationships are illustrative only.

A catalog is a JSON array of course objects:

- Required: `code` and `name` (non-empty strings), `units` (non-negative integer).
- Optional: `description` (string, defaults to `""`), `prerequisites` (defaults to
  `null`, meaning no prerequisites).
- A prerequisite is `{"type": "course", "course_code": "ECS 20"}`, or an object
  with `"type": "and"` / `"type": "or"` and a `"requirements"` array of prerequisite
  objects. Groups can nest recursively. Null children are invalid.
- Empty groups are allowed, matching the existing evaluator: empty AND is true;
  empty OR is false. Single-child groups retain their wrappers.
- Unknown fields, unsupported types, invalid values, and duplicate course codes
  are rejected with `ValueError`. Filesystem errors propagate normally.
- Course codes match exactly. References need not exist in the same file, allowing
  small or department-specific catalogs. Loading does not evaluate prerequisites.

From the backend Python import context:

```python
from pathlib import Path
from app.services.course_catalog import load_course_catalog

catalog = load_course_catalog(Path("app/data/courses/ecs.json"))
course = catalog["ECS SAMPLE 5"]
```

The result is a plain `dict[str, Course]`: indexing an absent code raises
`KeyError`; `catalog.get(code)` returns `None` for an absent code.
