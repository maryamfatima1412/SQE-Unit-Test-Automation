"""Run the test suites with one command (works the same on Windows, macOS and Linux).

    python run_tests.py                 -> list of suites
    python run_tests.py smoke           -> quick core checks
    python run_tests.py all             -> everything, one after the other, in the configured order
    python run_tests.py parallel        -> everything, in parallel on all CPU cores (pytest-xdist)

Task 4 - configuration:
  * suites     : name -> pytest options below (they use the markers declared in pytest.ini)
  * groups     : markers  smoke / grading / storage / student_analytics / data_driven / known_defects
  * parallel   : pytest-xdist  (-n auto); every test has its own temp data file, so tests cannot disturb each other
  * order      : tests/conftest.py  GROUP_ORDER + @pytest.mark.execution_order(n)
  * parameters : @pytest.mark.parametrize and the CSV files in tests/data
"""
import sys

import pytest

SUITES = {
    # --- by purpose -------------------------------------------------------------------------
    "smoke": (["-m", "smoke"], "small set of core checks"),
    "regression": (["-m", "not known_defects"], "all tests that must always pass (everything except known_defects)"),
    "known-defects": (["-m", "known_defects"], "tests that document real defects (xfail)"),
    "data-driven": (["-m", "data_driven"], "tests fed from CSV files listed in the Excel sheet"),
    "boundary": (["-m", "boundary"], "boundary value analysis tests"),
    "negative": (["-m", "negative"], "invalid input / error handling tests"),
    # --- by module --------------------------------------------------------------------------
    "grading": (["-m", "grading"], "Module 1 - grade_from_percentage / grade_color"),
    "storage": (["-m", "storage"], "Module 2 - Storage class"),
    "student-analytics": (["-m", "student_analytics"], "Module 3 - StudentDashboard"),
    # --- by person --------------------------------------------------------------------------
    "maryam": (["-m", "maryam"], "tests written by Maryam Fatima"),
    "huda": (["-m", "huda"], "tests written by Huda Asif"),
    # --- everything -------------------------------------------------------------------------
    "all": ([], "every test, sequential, in the configured group order"),
    "ordered": (["-v", "-p", "no:xdist"], "every test, sequential and verbose - shows the exact execution order"),
    "parallel": (["-n", "auto"], "every test in parallel on all CPU cores"),
    "coverage": (["--cov=student_portal", "--cov-report=term-missing", "--cov-report=html"],
                 "every test with a coverage report (htmlcov/index.html)"),
}


def main(argv):
    if not argv or argv[0] not in SUITES:
        print(__doc__)
        print("Available suites:")
        for name, (_opts, text) in SUITES.items():
            print(f"  {name:<18} {text}")
        return 0 if not argv else 2
    options, _text = SUITES[argv[0]]
    return pytest.main(options + argv[1:])  # extra arguments are passed to pytest, e.g.  -k attendance


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
