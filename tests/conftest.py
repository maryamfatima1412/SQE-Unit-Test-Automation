"""Shared fixtures and the execution-order configuration for the whole suite.

Task 4 (configuration) lives here and in pytest.ini:
  * GROUP_ORDER  -> order in which the test *groups* run
  * execution_order(n) marker -> order of test *cases* inside a group
  * fixtures that keep every test isolated, so tests are safe to run in parallel
"""
import datetime as _dt
from types import SimpleNamespace

import pytest

import student_portal as sp

# --------------------------------------------------------------------------- #
# Execution order
# --------------------------------------------------------------------------- #
# Groups run in this order. A test belongs to the first group (marker) it carries.
GROUP_ORDER = ["smoke", "grading", "storage", "student_analytics", "data_driven", "known_defects"]
DEFAULT_CASE_ORDER = 100


def pytest_collection_modifyitems(config, items):
    """Sort tests by (group order, execution_order marker). list.sort is stable, so
    tests with the same key keep their natural order (file order, then definition order)."""

    def sort_key(item):
        group = next((i for i, g in enumerate(GROUP_ORDER) if item.get_closest_marker(g)), len(GROUP_ORDER))
        marker = item.get_closest_marker("execution_order")
        case = marker.args[0] if marker and marker.args else DEFAULT_CASE_ORDER
        return group, case

    items.sort(key=sort_key)


# --------------------------------------------------------------------------- #
# Isolation: no test ever touches the real portal_data.json
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path, monkeypatch):
    """Point the application's DATA_FILE to a private temp file for every test.
    Each test (and each parallel worker) therefore has its own storage."""
    path = tmp_path / "portal_data.json"
    monkeypatch.setattr(sp, "DATA_FILE", str(path))
    return path


@pytest.fixture
def store(isolated_data_file):
    """A fresh Storage object with the default seed data."""
    return sp.Storage()


@pytest.fixture
def frozen_now(monkeypatch):
    """Freeze datetime.now() inside student_portal to 2026-10-15 12:00:00."""
    fixed = _dt.datetime(2026, 10, 15, 12, 0, 0)

    class FixedDateTime(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed

    monkeypatch.setattr(sp, "datetime", FixedDateTime)
    return fixed


# --------------------------------------------------------------------------- #
# Helpers for the StudentDashboard class (no Tk window is created)
# --------------------------------------------------------------------------- #
class FakeStore:
    """Minimal stand-in for Storage: only get(key) is needed by the dashboard."""

    def __init__(self, **tables):
        self.tables = tables

    def get(self, key):
        return self.tables.setdefault(key, [])


class FakeVar:
    """Stand-in for a tkinter StringVar (only get() is used)."""

    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


@pytest.fixture
def make_dashboard():
    """Factory that builds a StudentDashboard WITHOUT creating any Tk widgets.
    __new__ skips __init__ (which needs a real window); we set only the attributes
    the methods under test read."""

    def _make(roll="2024-001", course="CS101", store=None, att_filter="All Courses", res_filter=""):
        dash = sp.StudentDashboard.__new__(sp.StudentDashboard)
        dash.roll, dash.course = roll, course
        dash.store = store or FakeStore()
        dash.att_filter, dash.res_filter = FakeVar(att_filter), FakeVar(res_filter)
        dash.cw_tree, dash.log_tree, dash.res_tree, dash.mc_tree = "cw_tree", "log_tree", "res_tree", "mc_tree"
        return dash

    return _make


@pytest.fixture
def captured_tables(monkeypatch):
    """Replace fill_table() with a recorder so we can assert on the rows a method produces."""
    calls = []

    def fake_fill_table(tree, rows, empty_msg, extra_tags=None):
        calls.append(SimpleNamespace(tree=tree, rows=list(rows), empty_msg=empty_msg, tag=extra_tags))

    monkeypatch.setattr(sp, "fill_table", fake_fill_table)
    return calls


@pytest.fixture
def att_rec():
    """Builder: attendance record. att_rec('CS101', '2026-10-01', {'2024-001': 'present'})"""

    def _build(code, date, statuses):
        return {"courseCode": code, "date": date, "markedBy": "test", "timestamp": date + "T09:00:00",
                "students": [{"rollNo": r, "status": s} for r, s in statuses.items()]}

    return _build


@pytest.fixture
def res_rec():
    """Builder: results record. res_rec('CS101', 'midterm', 100, {'2024-001': (85, '85.00', 'A')})"""

    def _build(code, kind, total, entries, approved=True, timestamp="2026-10-02T10:00:00"):
        return {"courseCode": code, "assessmentType": kind, "totalMarks": total, "uploadedBy": "test",
                "timestamp": timestamp, "approved": approved,
                "students": [{"rollNo": r, "marks": m, "percentage": p, "grade": g} for r, (m, p, g) in entries.items()]}

    return _build


@pytest.fixture
def courses():
    return [{"code": "CS101", "name": "Introduction to Programming", "teacher": "Fatima Khan", "students": 15},
            {"code": "CS202", "name": "Data Structures", "teacher": "Ahmed Hassan", "students": 12}]
