"""Known defects found by unit testing (group: known_defects).

Each test states the CORRECT behaviour and is marked xfail with the defect ID, so the suite stays
green but the defect is documented and visible in the report ("xfailed").
Because pytest.ini sets xfail_strict = true, a test here that starts to PASS (the defect was fixed)
is reported as a failure -> then remove the xfail marker and keep it as a normal regression test.

Defect IDs:
  DEF-0xx   = already reported in the Assignment 2 Test Summary Report (unit-level evidence)
  UT-DEF-0x = new defects found while writing these unit tests
"""
import json

import pytest

import student_portal as sp

pytestmark = [pytest.mark.known_defects]


@pytest.mark.xfail(reason="UT-DEF-01: Storage() crashes with AttributeError when portal_data.json holds valid JSON "
                          "that is not an object (for example [] or null)", raises=AttributeError)
@pytest.mark.parametrize("content", ["[1, 2, 3]"])
def test_json_file_that_is_not_an_object_does_not_crash_the_app(isolated_data_file, content):
    """[EG] A damaged file with valid JSON of the wrong type should fall back to the seed data."""
    isolated_data_file.write_text(content, encoding="utf-8")
    assert len(sp.Storage().get("systemUsers")) == 6


@pytest.mark.xfail(reason="UT-DEF-02: save() opens the file with 'w' before json.dump(), so a serialisation error "
                          "leaves a truncated, unreadable data file on disk (all data lost)")
def test_failed_save_keeps_the_previous_file_valid(store, isolated_data_file):
    """[EG] After set() fails with TypeError the file on disk must still be valid JSON."""
    with pytest.raises(TypeError):
        store.set("bad", {1, 2})
    json.loads(isolated_data_file.read_text(encoding="utf-8"))


@pytest.mark.xfail(reason="UT-DEF-03: overall_attendance() rounds to a whole number, so 74.7 % becomes 75 % and the "
                          "dashboard (which checks pct < 75) shows no low-attendance warning")
def test_attendance_below_75_percent_is_not_rounded_up_to_75(make_dashboard, att_rec):
    """[BVA] 747 of 1000 classes = 74.7 % must stay below the 75 % limit."""
    records = [att_rec("CS101", "2026-10-01", {"2024-001": "present" if i < 747 else "absent"}) for i in range(1000)]
    _total, _present, percent = make_dashboard().overall_attendance(records)
    assert percent < 75


@pytest.mark.xfail(reason="DEF-014 (Assignment 2) / UT-DEF-04: grade_from_percentage has no input validation; a negative "
                          "percentage is graded 'F' and a percentage above 100 is graded 'A+' instead of being rejected")
def test_out_of_range_percentage_is_rejected():
    """[BVA] A percentage just below 0 or just above 100 is invalid and should raise ValueError."""
    for pct in (-0.01, 100.01):
        with pytest.raises(ValueError):
            sp.grade_from_percentage(pct)


@pytest.mark.xfail(reason="DEF-015 (Assignment 2): invalid values are silently accepted; NaN is graded 'F' instead of "
                          "being rejected")
def test_nan_percentage_is_rejected():
    """[EG] NaN is not a valid percentage and should raise ValueError."""
    with pytest.raises(ValueError):
        sp.grade_from_percentage(float("nan"))


@pytest.mark.xfail(reason="DEF-023 (Assignment 2): a corrupted data file is silently replaced by seed data; no backup "
                          "copy of the damaged file is kept")
def test_corrupt_data_file_is_backed_up_before_it_is_replaced(isolated_data_file, tmp_path):
    """[EG] After loading a corrupt file there should be a backup next to it, so nothing is lost silently."""
    isolated_data_file.write_text("{ not valid json", encoding="utf-8")
    sp.Storage()
    others = [p for p in tmp_path.iterdir() if p != isolated_data_file]
    assert others, "no backup of the corrupt file was created"
