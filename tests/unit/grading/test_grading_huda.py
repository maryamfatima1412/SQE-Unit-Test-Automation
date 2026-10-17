"""Module 1 - Grading logic (grade_from_percentage, grade_color).

Tests written by: Huda Asif (24F-3111)
Focus: invalid input, unusual values, error guessing and module-level properties.
Characterisation tests record what the code does today (for example "no validation of the
upper limit"); real defects are listed in tests/known_defects.
"""
import decimal
import fractions
import math
import re

import pytest

import student_portal as sp

pytestmark = [pytest.mark.grading, pytest.mark.huda]


class TestGradeFromPercentage:
    """Function under test: grade_from_percentage(p)."""

    @pytest.mark.negative
    @pytest.mark.parametrize("pct", [-0.01, -5])
    def test_negative_percentage_is_graded_f(self, pct):
        """[ECP-invalid] Values below the valid range 0..100 currently return F (no validation)."""
        assert sp.grade_from_percentage(pct) == "F"

    @pytest.mark.negative
    @pytest.mark.parametrize("pct", [100.01, 101])
    def test_percentage_above_100_is_graded_a_plus(self, pct):
        """[ECP-invalid] Values above 100 currently return A+ (there is no upper limit check)."""
        assert sp.grade_from_percentage(pct) == "A+"

    @pytest.mark.boundary
    def test_floating_point_values_next_to_a_cutoff(self):
        """[BVA] Tiny differences around the 90 cut-off decide the grade correctly."""
        assert sp.grade_from_percentage(89.9999999) == "A"
        assert sp.grade_from_percentage(90.0000001) == "A+"

    @pytest.mark.negative
    def test_nan_is_graded_f_without_an_error(self):
        """[EG] NaN fails every comparison, so it silently becomes F."""
        assert sp.grade_from_percentage(float("nan")) == "F"

    @pytest.mark.negative
    @pytest.mark.parametrize("bad", [None, "90"])
    def test_non_numeric_input_raises_type_error(self, bad):
        """[ECP-invalid] None, text, list and dict are not numbers and raise TypeError."""
        with pytest.raises(TypeError):
            sp.grade_from_percentage(bad)


class TestGradeColor:
    """Function under test: grade_color(grade)."""

    @pytest.mark.negative
    @pytest.mark.parametrize("placeholder", ["-", ""])
    def test_placeholder_or_empty_grade_is_red(self, placeholder):
        """[ECP-invalid] The '-' shown before marks are entered, and '', fall through to RED."""
        assert sp.grade_color(placeholder) == sp.RED

    @pytest.mark.negative
    @pytest.mark.parametrize("grade", ["a", "a+"])
    def test_lowercase_grades_are_not_recognised(self, grade):
        """[EG] The check is case-sensitive, so lowercase grades are RED."""
        assert sp.grade_color(grade) == sp.RED

    @pytest.mark.negative
    @pytest.mark.parametrize("grade", [" A", " B+"])
    def test_grade_with_leading_whitespace_is_red(self, grade):
        """[EG] A grade that starts with a space or tab does not match 'A'/'B'/'C'."""
        assert sp.grade_color(grade) == sp.RED

    @pytest.mark.negative
    @pytest.mark.parametrize("bad", [None, 5])
    def test_non_string_input_raises_attribute_error(self, bad):
        """[ECP-invalid] startswith() does not exist on non-strings, so AttributeError is raised."""
        with pytest.raises(AttributeError):
            sp.grade_color(bad)

    def test_any_text_starting_with_a_is_green(self):
        """[EG] Characterisation: the function checks only the first letter, so 'Apple' is GREEN."""
        assert sp.grade_color("Apple") == sp.GREEN
        assert sp.grade_color("Banana") == sp.BLUE


class TestGradingModule:
    """Module-level behaviour of the grading scale."""

    def test_colour_constants_are_distinct_hex_codes(self):
        """[ECP] GREEN, BLUE, ORANGE and RED are four different #rrggbb values."""
        colours = [sp.GREEN, sp.BLUE, sp.ORANGE, sp.RED]
        assert len(set(colours)) == 4
        assert all(re.fullmatch(r"#[0-9a-f]{6}", c) for c in colours)

    def test_functions_are_deterministic(self):
        """[EG] Calling 1000 times with the same input always gives the same output (no hidden state)."""
        assert {sp.grade_from_percentage(77.5) for _ in range(1000)} == {"B+"}
        assert {sp.grade_color("B+") for _ in range(1000)} == {sp.BLUE}

    @pytest.mark.parametrize("value", [decimal.Decimal("85"), fractions.Fraction(85)])
    def test_accepts_any_numeric_type(self, value):
        """[ECP] int, float, Decimal and Fraction behave the same for the same value."""
        assert sp.grade_from_percentage(value) == "A"

    @pytest.mark.boundary
    def test_extreme_magnitudes_and_infinity(self):
        """[BVA] Huge numbers and +-infinity are clamped by the comparisons (A+ / F)."""
        assert sp.grade_from_percentage(1e308) == "A+"
        assert sp.grade_from_percentage(math.inf) == "A+"
        assert sp.grade_from_percentage(-1e308) == "F"
        assert sp.grade_from_percentage(-math.inf) == "F"

    @pytest.mark.parametrize("marks, total, grade, colour", [(0, 20, "F", "RED"), (10, 20, "C-", "ORANGE")])
    def test_marks_to_colour_pipeline_including_total_of_one(self, marks, total, grade, colour):
        """[BVA] marks -> percentage -> grade -> colour, including the smallest total (1)."""
        g = sp.grade_from_percentage(marks / total * 100)
        assert g == grade
        assert sp.grade_color(g) == getattr(sp, colour)
