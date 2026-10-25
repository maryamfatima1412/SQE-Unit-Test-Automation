---
title: "Unit Test Automation - Summary Report"
subtitle: "Student Portal - Attendance & Result Management System"
author: "Maryam Fatima (24F-3044), Huda Asif (24F-3111) - BSE-5A, Fall 2026"
---

# 1. Objective
Build an automated unit-test solution (Python / pytest) for the Student Portal application that was tested manually in Assignment 2,
using equivalence class partitioning, boundary value analysis and error guessing, with data-driven tests, groups, parallel runs and a fixed execution order.

# 2. Environment (Task 1)
| Item | Value |
|---|---|
| Application | `src/student_portal.py` (Tkinter + JSON storage), unchanged |
| Python | 3.12 (virtual environment) |
| Packages | pytest 9.1, pytest-xdist, pytest-cov, openpyxl |
| Setup | `docs/Setup_Guide.md`; video in `docs/video/` (script in `docs/Video_Script.md`) |

# 3. Modules and tests (Task 2)
| Module | Units tested | Tests (incl. data-driven runs) |
|---|---|---|
| 1. Grading | `grade_from_percentage`, `grade_color`, grading module | 48 |
| 2. Storage | `get`, `set`, `log_activity`, `Storage` class / start-up | 41 |
| 3. Student analytics | `overall_attendance`, `average_grade`, `load_course_wise_attendance`, `StudentDashboard` class (filters, my courses) | 45 |
| Known defects | xfail tests documenting defects | 6 |

* **Every function and every class has 5 tests per person** (verified by the sheet *Coverage Check*: all 11 rows "OK").
* The Excel inventory lists 111 unit test functions. Together with the data-driven tests (CSV rows) and parametrized cases, the suite runs **166 tests: 160 passed, 6 expected failures (xfail), 0 failed**.
* Technique notes (ECP, BVA, error guessing, state): `docs/Test_Design_Notes.md`. Every test docstring carries a tag `[ECP]`, `[BVA]` or `[EG]`.
* The GUI is tested without opening a window: the dashboard object is created with `__new__`, with a fake storage and a recorder instead of the table widget.

# 4. Data-driven tests (Task 3)
Five test cases are defined in the Excel sheet *Data Driven Cases* (`docs/Unit_Test_Cases.xlsx`); each reads an external CSV file:

| ID | Function | CSV | Runs |
|---|---|---|---|
| DD-01 | grade_from_percentage | grade_boundaries.csv | 6 |
| DD-02 | grade_color | grade_colors.csv | 4 |
| DD-03 | overall_attendance | attendance_cases.csv | 5 |
| DD-04 | average_grade | average_grade_cases.csv | 5 |
| DD-05 | Storage set/get | storage_roundtrip.csv | 4 |

New data = new CSV row, no code change.

# 5. Configuration (Task 4)
| Requirement | Implementation |
|---|---|
| Suites | `run_tests.py`: smoke, regression, known-defects, data-driven, boundary, negative, grading, storage, student-analytics, maryam, huda, all, ordered, parallel, coverage |
| Groups | pytest markers declared in `pytest.ini` (`--strict-markers`) |
| Parallel | `pytest -n auto` (xdist); each test has its own temp data file, so there is no interference |
| Order | smoke, grading, storage, student_analytics, data_driven, known_defects; inside a group by `@pytest.mark.execution_order(n)` (hook in `tests/conftest.py`) |
| Parameterization | `@pytest.mark.parametrize` + CSV files |
| CI (optional) | `.github/workflows/tests.yml` |

# 6. Results
| Run | Result |
|---|---|
| Sequential (`all`) | 160 passed, 6 xfailed, about 1-5 s |
| Parallel (`parallel`) | same result |
| Smoke | passes first in the order |

## Coverage (pytest-cov, `student_portal.py`)
* Tested functions and classes: about **100 %** of their lines.
* Whole file: **24 %** (1004 statements, 764 not executed). The untested part is the Tkinter user interface (windows, buttons, dialogs, PDF export), which cannot be unit tested without a display and was covered by the manual tests of Assignment 2.

# 7. Defects found (xfail tests)
| ID | Where | Description |
|---|---|---|
| UT-DEF-01 | `Storage()` | A data file that is valid JSON but not an object (`[]`, `null`, `42`, text) crashes the start-up  |
| UT-DEF-02 | `Storage.save/set` | A value that cannot be saved as JSON truncates the file; all stored data is lost |
| UT-DEF-03 | `overall_attendance` | 747 of 1000 (74.7 %) is rounded to 75 %, so the "below 75 %" warning is hidden |
| DEF-014 / UT-DEF-04 | `grade_from_percentage` | Negative percentage gets grade F and a percentage above 100 gets A+ instead of being rejected |
| DEF-015 | `grade_from_percentage` | NaN gets grade F instead of being rejected |
| DEF-023 | `Storage()` | A corrupt data file is silently replaced by seed data, no backup |

DEF-ids come from the Assignment 2 report; UT-DEF-ids are new, found by the unit tests. Strict xfail means: once a defect is fixed the test reports it and the marker can be removed.

# 8. Team work
| Person | Work |
|---|---|
| Maryam Fatima | Tests for valid classes and boundaries (`*_maryam.py`), Excel sheet and CSV data, `pytest.ini`, `conftest.py`, `run_tests.py` |
| Huda Asif | Tests for invalid and unusual input (`*_huda.py`), known-defect tests, documentation (notes, README, setup guide) |
The Git history of the repository shows the individual commits (see `docs/COMMIT_PLAN.md`).

# 9. Limitations and next steps
* GUI code (about 76 % of the file) is not covered; a GUI test tool or refactoring the logic out of the GUI classes would raise coverage.
* Defects above should be fixed and the `xfail` markers removed.
* Tests rely on a few internals of the application (`sp.DATA_FILE`), so renaming them requires updating `conftest.py`.
