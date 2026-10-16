"""Module 1 - Grading logic (grade_from_percentage, grade_color).

Tests written by: Maryam Fatima (24F-3044)
Focus: valid equivalence classes (ECP) and boundary values (BVA).
Each test has a docstring starting with its design technique: [ECP], [BVA], [EG] (error guessing).
"""
import re

import pytest

import student_portal as sp

pytestmark = [pytest.mark.grading, pytest.mark.maryam]

ALL_GRADES = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "F"]


class TestGradeFromPercentage:
    """Function under test: grade_from_percentage(p)."""

    @pytest.mark.smoke
    @pytest.mark.boundary
    @pytest.mark.execution_order(1)
    @pytest.mark.parametrize("pct, grade", [(90, "A+"), (80, "A-"), (60, "C+"), (50, "C-")])
    def test_value_exactly_on_a_cutoff_gets_the_higher_grade(self, pct, grade):
        """[BVA] On-boundary values: a percentage equal to a cut-off belongs to the higher grade."""
        assert sp.grade_from_percentage(pct) == grade

    @pytest.mark.boundary
    @pytest.mark.parametrize("pct, grade", [(89.99, "A"), (69.99, "B-"), (49.99, "F")])
    def test_value_just_below_a_cutoff_gets_the_lower_grade(self, pct, grade):
        """[BVA] Off-boundary values: 0.01 below each cut-off falls into the next lower grade."""
        assert sp.grade_from_percentage(pct) == grade

    @pytest.mark.equivalence
    @pytest.mark.parametrize("pct, grade", [(95, "A+"), (72, "B"), (25, "F")])
    def test_typical_value_inside_each_grade_band(self, pct, grade):
        """[ECP] One representative value from the middle of every valid grade band."""
        assert sp.grade_from_percentage(pct) == grade

    @pytest.mark.boundary
    def test_extreme_valid_values_0_and_100(self):
        """[BVA] The two ends of the valid range 0..100."""
        assert sp.grade_from_percentage(0) == "F"
        assert sp.grade_from_percentage(100) == "A+"

    @pytest.mark.equivalence
    def test_every_whole_percentage_returns_a_known_grade(self):
        """[ECP] Output domain: every whole percentage 0..100 maps to one of the 10 defined grades."""
        assert all(sp.grade_from_percentage(p) in ALL_GRADES for p in range(0, 101))


class TestGradeColor:
    """Function under test: grade_color(grade)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    @pytest.mark.parametrize("grade", ["A"])
    def test_a_grades_are_green(self, grade):
        """[ECP] Class 'A family' -> GREEN."""
        assert sp.grade_color(grade) == sp.GREEN

    @pytest.mark.equivalence
    @pytest.mark.parametrize("grade", ["B"])
    def test_b_grades_are_blue(self, grade):
        """[ECP] Class 'B family' -> BLUE."""
        assert sp.grade_color(grade) == sp.BLUE

    @pytest.mark.equivalence
    @pytest.mark.parametrize("grade", ["C"])
    def test_c_grades_are_orange(self, grade):
        """[ECP] Class 'C family' -> ORANGE."""
        assert sp.grade_color(grade) == sp.ORANGE

    @pytest.mark.equivalence
    def test_fail_grade_is_red(self):
        """[ECP] Class 'fail' -> RED."""
        assert sp.grade_color("F") == sp.RED

    @pytest.mark.equivalence
    @pytest.mark.parametrize("grade", ["A+", "C", "F"])
    def test_every_grade_returns_a_hex_colour_code(self, grade):
        """[ECP] The result is always a valid #rrggbb colour string."""
        assert re.fullmatch(r"#[0-9a-f]{6}", sp.grade_color(grade))


class TestGradingModule:
    """Module-level behaviour: the two functions working together as the grading scale."""

    @pytest.mark.smoke
    @pytest.mark.execution_order(2)
    def test_scale_is_monotonic_a_higher_percentage_never_gives_a_lower_grade(self):
        """[BVA] Walking from 0 to 100 in steps of 0.5 the grade rank never goes down."""
        rank = {g: i for i, g in enumerate(reversed(ALL_GRADES))}  # F=0 ... A+=9
        previous = -1
        for step in range(0, 201):
            current = rank[sp.grade_from_percentage(step / 2)]
            assert current >= previous
            previous = current

    def test_scale_has_exactly_ten_distinct_grades(self):
        """[ECP] Across 0..100 all 10 grades are reachable and no other value appears."""
        assert {sp.grade_from_percentage(p) for p in range(0, 101)} == set(ALL_GRADES)

    @pytest.mark.boundary
    def test_pass_fail_line_is_at_50_percent(self):
        """[BVA] 50 is the lowest passing mark (C-), 49 and below is F."""
        assert all(sp.grade_from_percentage(p) != "F" for p in range(50, 101))
        assert all(sp.grade_from_percentage(p) == "F" for p in range(0, 50))

    def test_colour_bands_follow_percentage_ranges(self):
        """[ECP] >=80 green, 65-79 blue, 50-64 orange, <50 red, for every whole percentage."""
        for p in range(0, 101):
            expected = sp.GREEN if p >= 80 else sp.BLUE if p >= 65 else sp.ORANGE if p >= 50 else sp.RED
            assert sp.grade_color(sp.grade_from_percentage(p)) == expected, p

    def test_marks_to_grade_pipeline_for_typical_exams(self):
        """[ECP] The app computes marks / total * 100 and then the grade; check realistic exams."""
        cases = [(45, 50, "A+"), (17, 20, "A"), (32, 40, "A-"), (60, 80, "B+"), (14, 20, "B"),
                 (13, 20, "B-"), (12, 20, "C+"), (11, 20, "C"), (10, 20, "C-"), (9, 20, "F")]
        for marks, total, grade in cases:
            assert sp.grade_from_percentage(marks / total * 100) == grade, (marks, total)
