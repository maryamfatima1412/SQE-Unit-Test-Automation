# SQE Assignment 3 - Unit Test Automation (Student Portal)

Automated unit tests (pytest) for the **Student Portal - Attendance & Result Management System** (the application tested manually in Assignment 2).

| | |
|---|---|
| Course | Software Quality Engineering (BSE-5A, Fall 2026) |
| Team | Maryam Fatima (24F-3044), Huda Asif (24F-3111) |
| Application | `src/student_portal.py` (unchanged copy of the Assignment 2 app) |
| Tools | Python 3.12, pytest, pytest-xdist, pytest-cov, openpyxl |

## Result at a glance
* **160 tests pass, 6 tests are expected failures (xfail)** that document real defects found by the unit tests.
* 3 modules, 11 units under test (each function and each class with 5 tests per person).
* Data-driven tests: 5 cases in Excel, data in 5 CSV files (24 runs).
* Coverage: about 100 % of the tested functions/classes, about 24 % of the whole file (the Tkinter GUI is not unit tested).

## Modules under test
1. **Grading** - `grade_from_percentage`, `grade_color`
2. **Storage** - `Storage.get`, `set`, `log_activity`, start-up / `initialize_all_data`
3. **Student analytics** - `StudentDashboard.overall_attendance`, `average_grade`, `load_course_wise_attendance`, `filter_attendance_log`, `filter_course_results`, `load_my_courses`

## Setup (about 2 minutes)
```bash
git clone <repo-url>
cd SQE-Unit-Test-Automation
python -m venv venv
# Windows:  venv\Scripts\activate        Linux/macOS:  source venv/bin/activate
pip install -r requirements.txt
python run_tests.py smoke
```
tkinter is needed because `student_portal.py` imports it (included with Python on Windows/macOS; on Ubuntu: `sudo apt install python3-tk`
and create the venv with `--system-site-packages`). More details: `docs/Setup_Guide.md`.

## Running the tests
| Command | What it does |
|---|---|
| `python run_tests.py` | list all suites |
| `python run_tests.py smoke` | quick core checks |
| `python run_tests.py all` | everything in the configured order |
| `python run_tests.py parallel` | everything in parallel (`pytest -n auto`) |
| `python run_tests.py regression` | everything that must pass (no known defects) |
| `python run_tests.py known-defects` | tests that document real defects (xfail) |
| `python run_tests.py data-driven` | Excel + CSV driven tests |
| `python run_tests.py grading` / `storage` / `student-analytics` | one module |
| `python run_tests.py maryam` / `huda` | tests of one person |
| `python run_tests.py boundary` / `negative` | by technique |
| `python run_tests.py ordered` | verbose, shows the execution order |
| `python run_tests.py coverage` | coverage report in `htmlcov/index.html` |

Extra pytest arguments can be added, e.g. `python run_tests.py all -k attendance`. Plain `pytest` also works.

## Task 4 - configuration (where to look)
| Requirement | Where |
|---|---|
| Different suites | `run_tests.py` (`SUITES`) |
| Groups | markers in `pytest.ini` (`smoke`, `grading`, `storage`, `student_analytics`, `data_driven`, `known_defects`, `boundary`, `negative`, `maryam`, `huda`) |
| Parallel runs | `pytest-xdist`, `-n auto`; every test uses its own temp data file (`tests/conftest.py`, fixture `isolated_data_file`) |
| Execution order | `tests/conftest.py` - `GROUP_ORDER` + `@pytest.mark.execution_order(n)` |
| Parameterization | `@pytest.mark.parametrize` in the tests and CSV files in `tests/data` |

## Project structure
```
src/student_portal.py              application under test (unchanged)
tests/conftest.py                  fixtures, execution-order hook
tests/unit/grading/                Module 1 (Maryam + Huda files)
tests/unit/storage/                Module 2
tests/unit/student_analytics/      Module 3
tests/known_defects/               xfail tests = defects found
tests/data_driven/                 Excel + CSV driven tests
tests/data/*.csv                   external test data
docs/Unit_Test_Cases.xlsx          Excel: data-driven cases, test inventory, coverage check, defects
docs/Test_Design_Notes.md          ECP / BVA notes per module
docs/Summary_Report.md / .docx     summary report
docs/Setup_Guide.md, Video_Script.md, COMMIT_PLAN.md
docs/video/                        setup video (recorded by the team)
tools/generate_excel.py            builds the Excel sheet
run_tests.py, pytest.ini, requirements.txt
.github/workflows/tests.yml        optional CI
```

## Who did what
* **Maryam Fatima** - `*_maryam.py` files: valid classes, normal behaviour, boundary values; Excel sheet and test configuration.
* **Huda Asif** - `*_huda.py` files: invalid input, error handling and unusual data; documentation and known-defect analysis.
Each person has 5 tests for every function and 5 for every class/module (see sheet *Coverage Check*). The Git history shows the individual commits.

## Known defects found by unit tests
See `tests/known_defects/test_known_defects.py` and the sheet *Known Defects*. They run as `xfail(strict)`: when a defect is fixed, the test
turns red until the marker is removed, so the fix is noticed.
