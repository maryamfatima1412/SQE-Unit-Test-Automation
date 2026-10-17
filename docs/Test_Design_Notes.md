# Test Design Notes (ECP, BVA and other techniques)

**Project:** Student Portal - Attendance & Result Management System (`src/student_portal.py`)
**Authors:** Maryam Fatima (24F-3044), Huda Asif (24F-3111)
**Assignment 3 - Task 2:** notes on what we test for each module, before/while writing the automated unit tests.

Techniques used (the tag in every test docstring shows which one it is):

| Tag | Technique | Idea |
|---|---|---|
| ECP | Equivalence class partitioning | Split the inputs into classes that the code treats the same; test one value per class. `ECP-invalid` = a class of invalid input. |
| BVA | Boundary value analysis | Test the values on and next to the edges of each class (min, min+1, max-1, max, just below/above a cut-off). |
| EG | Error guessing | Inputs where experience says developers make mistakes (empty data, NaN, wrong type, damaged files, duplicates, unicode). |
| State | State / persistence | Test what is remembered between calls and across an application restart. |

How the work is shared: **Maryam** writes the normal behaviour and the boundary tests (valid classes); **Huda** writes the invalid,
unusual and error-handling tests. Every function has **5 tests per person**, and every class / module has **5 tests per person**
on top of that (see `docs/Unit_Test_Cases.xlsx`, sheet *Coverage Check*).

How the three modules were chosen: they are the parts of the application with real logic that can be tested **without opening a
window**, and each one is behind a feature that failed in the Assignment 2 manual testing.

| # | Module | Why it was chosen | Related Assignment 2 defects |
|---|---|---|---|
| 1 | Grading (`grade_from_percentage`, `grade_color`) | Pure functions with many boundaries (10 grades) | DEF-014, DEF-015 |
| 2 | `Storage` class (`get`, `set`, `log_activity`, start-up) | Every feature depends on it; all data is saved here | DEF-023 |
| 3 | `StudentDashboard` class (`overall_attendance`, `average_grade`, `load_course_wise_attendance`, filters) | The 75 % warning and the average grade come from these calculations | DEF-018, DEF-019 |

---

## Module 1 - Grading

### `grade_from_percentage(p)`
Rule (from the code): `>=90 A+`, `>=85 A`, `>=80 A-`, `>=75 B+`, `>=70 B`, `>=65 B-`, `>=60 C+`, `>=55 C`, `>=50 C-`, otherwise `F`.

**Equivalence classes**

| Class | Range | Expected | Valid? | Representative value |
|---|---|---|---|---|
| E1 | 90 - 100 | A+ | valid | 95 |
| E2 | 85 - <90 | A | valid | 87 |
| E3 | 80 - <85 | A- | valid | 82 |
| E4 | 75 - <80 | B+ | valid | 77 |
| E5 | 70 - <75 | B | valid | 72 |
| E6 | 65 - <70 | B- | valid | 67 |
| E7 | 60 - <65 | C+ | valid | 62 |
| E8 | 55 - <60 | C | valid | 57 |
| E9 | 50 - <55 | C- | valid | 52 |
| E10 | 0 - <50 | F | valid | 25 |
| E11 | < 0 | should be rejected | invalid | -5 |
| E12 | > 100 | should be rejected | invalid | 150 |
| E13 | not a number (None, text, list) | TypeError | invalid | `None`, `"90"` |
| E14 | NaN | should be rejected | invalid | `nan` |

**Boundary values** - for each of the 9 cut-offs *c*: `c-0.01` (lower grade), `c` (higher grade), `c+0.01`; plus the ends 0, 0.01, 100 and
the just-outside values -0.01 and 100.01; floating point `89.9999999` / `90.0000001`; extremes `1e308`, `inf`, `-inf`.

**What we test (10 tests, 5 per person):** on-cut-off values, just-below values, one value per class, 0 and 100, every whole percentage
(Maryam); negatives, above 100, floating-point neighbours, NaN, non-numeric types (Huda).
**Findings:** E11, E12 and E14 are accepted instead of rejected (DEF-014, UT-DEF-04, DEF-015).

### `grade_color(grade)`
| Class | Input | Expected |
|---|---|---|
| E1 | `A+`, `A`, `A-` | GREEN |
| E2 | `B+`, `B`, `B-` | BLUE |
| E3 | `C+`, `C`, `C-` | ORANGE |
| E4 | `F` | RED |
| E5 (invalid) | `-`, empty, lowercase, leading space, not a string | RED / AttributeError |

**Tests:** one test per family + hex-format check (Maryam); placeholder, lowercase, whitespace, non-string and the "first letter only" behaviour (Huda).

### Module level (the grading scale as a whole)
Monotonic scale (a higher percentage never gives a lower grade), exactly 10 distinct grades, pass/fail line at 50, colour bands per
percentage range, marks -> percentage -> grade pipeline (Maryam); constants, determinism, numeric types (int/float/Decimal/Fraction),
extreme magnitudes, pipeline with total marks of 1 (Huda).

---

## Module 2 - `Storage` class

Data is a dictionary saved as JSON in `portal_data.json` (tests use a private temp file, never the real one).

### `get(key)`  (`setdefault(key, [])`)
| Class | Input | Expected |
|---|---|---|
| E1 | existing key | stored value (same object) |
| E2 | missing key | `[]` and the key is created |
| E3 | non-list value (`dataVersion`) | returned unchanged |
| E4 (boundary/EG) | empty-string key, unicode key | works like a normal key |

State checks: `get()` does not write the file; changes made through the returned list are saved only after `save()`.

### `set(key, value)`
| Class | Input | Expected |
|---|---|---|
| E1 | list, dict, int, str, bool, float | stored in memory **and** written to the file at once |
| E2 | existing key | overwritten |
| E3 | `None` | stored as `null`; `get()` returns `None` |
| E4 (invalid) | not JSON serialisable (`set`) | `TypeError` |
| E5 (invalid) | file location not writable | message printed, no crash |

Persistence: a new `Storage()` (= application restart) must return the same value, also for Urdu text.
**Finding:** after the `TypeError` the file on disk is truncated and unreadable (UT-DEF-02).

### `log_activity(action, user)`
Boundary: 0 entries (list missing), 8 seeded, +1 per call, +100 (no size limit). Classes: normal text, empty text, unicode. Time format
`YYYY-MM-DD HH:MM:SS`, checked with a frozen clock. Saved to the file after every call.

### Class level - start-up (`__init__` + `initialize_all_data`)
| Situation | Expected |
|---|---|
| No file | seed data: 6 users, 3 courses, 3 students, 10 attendance, 4 results, 8 activities, `dataVersion = 2.0` |
| Valid current file | data kept, missing tables added, nothing re-seeded |
| Old `dataVersion` | everything cleared (documented behaviour; data-loss risk) |
| Empty or corrupt JSON | seed data (silent) - DEF-023 |
| Valid JSON that is not an object (`[]`, `null`, `42`) | should not crash - UT-DEF-01 |
| Calling `initialize_all_data()` twice | no change (idempotent) |

---

## Module 3 - `StudentDashboard` class

The dashboard object is created with `__new__` (no Tk window) and `fill_table()` is replaced by a recorder, so the calculations are
tested as plain functions.

### `overall_attendance(records)` -> `(total, present, percent)`
Rule: only the logged-in student's rows count; `present` and `late` count as attended; everything else is absent; percent = `round(present/total*100)`.

| Class | Input | Expected |
|---|---|---|
| E1 | all present | 100 % |
| E2 | mix of present / late / absent | late counts as present |
| E3 | no records, or student in no record | `(0, 0, 0)` - no division by zero |
| E4 | unknown status (`excused`, `PRESENT`, empty) | counts as absent |
| E5 | several courses | added together |
| E6 (invalid) | record without `students` | `KeyError` |

**Boundary values (75 % warning limit):** 73, 74, 75, 76 % (3/4 = 75, 37/50 = 74, 38/50 = 76, 74/100, 75/100); 0 records; 1 record.
**Finding:** 747/1000 = 74.7 % is rounded to 75 %, so the "below 75 %" warning is not shown (UT-DEF-03).

### `average_grade(records)` -> `(grade, count, average)`
Classes: one result, several results, unapproved results (ignored), other students' results (ignored), no results (`('-', 0, 0)`),
non-numeric percentage (`ValueError`). Boundary: the average exactly on 90 (80 and 100) and 0.01 below (89.98).
Rule noticed: a plain mean of percentages, not weighted by total marks (18/20 and 40/100 give 65 %).

### `load_course_wise_attendance(records, courses)`
Row = `(code, name, total, present, absent, "NN%", "Good"/"Low")`. Boundary: 74 % -> Low, 75 % -> Good, 0 % and 100 %, rounding 2/3 -> 67 %.
Classes: one course, two courses (order of first record), unknown course code (`Unknown`), no records (empty message), other student's records.

### Class level - filters and course list
`filter_attendance_log` (newest first, filter by course, status shown with a capital letter), `filter_course_results` (formatted row, no course
selected, unapproved and other students' results hidden), `load_my_courses` (percentage per course, no courses, a course without classes,
attendance of other courses ignored).

---

## Data-driven tests (Task 3)
Test cases are written in `docs/Unit_Test_Cases.xlsx` (sheet *Data Driven Cases*), each with a CSV file in `tests/data`:

| ID | Function | CSV file | Rows |
|---|---|---|---|
| DD-01 | `grade_from_percentage` | `grade_boundaries.csv` | 6 |
| DD-02 | `grade_color` | `grade_colors.csv` | 4 |
| DD-03 | `overall_attendance` | `attendance_cases.csv` | 5 |
| DD-04 | `average_grade` | `average_grade_cases.csv` | 5 |
| DD-05 | `Storage.set/get` | `storage_roundtrip.csv` | 4 |

`tests/data_driven/test_excel_driven.py` reads the Excel sheet and runs every CSV row as one test (24 test runs).

## Out of scope for unit testing
Tkinter windows (buttons, dialogs, layout), PDF export (`write_pdf`) and the login screen need a display; they were covered by the manual
tests of Assignment 2. Unit-test coverage is therefore high for the three modules and low for the whole file (see the summary report).
