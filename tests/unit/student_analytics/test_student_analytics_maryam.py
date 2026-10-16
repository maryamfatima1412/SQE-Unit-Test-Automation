"""Module 3 - StudentDashboard calculations and table builders (class StudentDashboard).

Tests written by: Maryam Fatima (24F-3044)
Focus: normal cases (valid equivalence classes) and the 75 % / grade boundaries.
No Tk window is opened: tests/conftest.py builds the object with __new__ and replaces fill_table()
with a recorder, so the logic can be tested as a pure unit.
"""
import pytest

pytestmark = [pytest.mark.student_analytics, pytest.mark.maryam]

ME = "2024-001"
OTHER = "2024-002"


class TestOverallAttendance:
    """Function under test: StudentDashboard.overall_attendance(records) -> (total, present, percent)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    @pytest.mark.execution_order(1)
    def test_all_classes_attended_gives_100_percent(self, make_dashboard, att_rec):
        """[ECP] Four records, all present -> (4, 4, 100)."""
        records = [att_rec("CS101", f"2026-10-0{i}", {ME: "present"}) for i in range(1, 5)]
        assert make_dashboard().overall_attendance(records) == (4, 4, 100)

    @pytest.mark.equivalence
    def test_late_counts_as_present_and_absent_does_not(self, make_dashboard, att_rec):
        """[ECP] present, late, absent, present -> 3 of 4 attended = 75 %."""
        statuses = ["present", "late", "absent", "present"]
        records = [att_rec("CS101", f"2026-10-0{i}", {ME: s}) for i, s in enumerate(statuses, 1)]
        assert make_dashboard().overall_attendance(records) == (4, 3, 75)

    @pytest.mark.boundary
    @pytest.mark.parametrize("present, total, percent", [(3, 4, 75), (37, 50, 74), (38, 50, 76), (75, 100, 75)])
    def test_percentages_around_the_75_percent_limit(self, make_dashboard, att_rec, present, total, percent):
        """[BVA] 74 %, 75 % and 76 % are calculated exactly (the dashboard warns below 75)."""
        records = [att_rec("CS101", "2026-10-01", {ME: "present" if i < present else "absent"}) for i in range(total)]
        assert make_dashboard().overall_attendance(records) == (total, present, percent)

    @pytest.mark.equivalence
    def test_records_of_other_students_are_ignored(self, make_dashboard, att_rec):
        """[ECP] A record that also lists another student counts only the logged-in student's row."""
        records = [att_rec("CS101", "2026-10-01", {OTHER: "absent", ME: "present"})]
        assert make_dashboard().overall_attendance(records) == (1, 1, 100)

    @pytest.mark.equivalence
    def test_records_of_several_courses_are_added_together(self, make_dashboard, att_rec):
        """[ECP] Overall attendance is across all courses: 1 of 2 in CS101 + 2 of 2 in CS202 = 3 of 4."""
        records = [att_rec("CS101", "2026-10-01", {ME: "present"}), att_rec("CS101", "2026-10-02", {ME: "absent"}),
                   att_rec("CS202", "2026-10-01", {ME: "present"}), att_rec("CS202", "2026-10-02", {ME: "late"})]
        assert make_dashboard().overall_attendance(records) == (4, 3, 75)


class TestAverageGrade:
    """Function under test: StudentDashboard.average_grade(records) -> (grade, count, average_percent)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    def test_single_result_gives_its_own_grade(self, make_dashboard, res_rec):
        """[ECP] One approved result of 85 % -> ('A', 1, 85.0)."""
        records = [res_rec("CS101", "midterm", 100, {ME: (85, "85.00", "A")})]
        assert make_dashboard().average_grade(records) == ("A", 1, 85.0)

    @pytest.mark.equivalence
    def test_average_of_two_results(self, make_dashboard, res_rec):
        """[ECP] 85 % and 90 % -> average 87.5 % -> grade A, count 2."""
        records = [res_rec("CS101", "midterm", 100, {ME: (85, "85.00", "A")}),
                   res_rec("CS101", "quiz", 20, {ME: (18, "90.00", "A")})]
        assert make_dashboard().average_grade(records) == ("A", 2, 87.5)

    @pytest.mark.boundary
    def test_average_exactly_on_the_a_plus_cutoff(self, make_dashboard, res_rec):
        """[BVA] 80 % and 100 % average to exactly 90 % which is A+."""
        records = [res_rec("CS101", "midterm", 100, {ME: (80, "80.00", "A-")}),
                   res_rec("CS101", "final", 100, {ME: (100, "100.00", "A+")})]
        assert make_dashboard().average_grade(records)[0] == "A+"

    @pytest.mark.boundary
    def test_average_just_below_the_a_plus_cutoff(self, make_dashboard, res_rec):
        """[BVA] 89.98 % average is still A (one hundredth below the cut-off)."""
        records = [res_rec("CS101", "midterm", 100, {ME: (80, "79.98", "B+")}),
                   res_rec("CS101", "final", 100, {ME: (100, "100.00", "A+")})]
        assert make_dashboard().average_grade(records)[0] == "A"

    @pytest.mark.equivalence
    def test_unapproved_results_are_not_counted(self, make_dashboard, res_rec):
        """[ECP] A result with approved=False is ignored: only the approved 70 % counts."""
        records = [res_rec("CS101", "midterm", 100, {ME: (70, "70.00", "B")}),
                   res_rec("CS101", "final", 100, {ME: (100, "100.00", "A+")}, approved=False)]
        assert make_dashboard().average_grade(records) == ("B", 1, 70.0)


class TestLoadCourseWiseAttendance:
    """Function under test: StudentDashboard.load_course_wise_attendance(records, courses)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    def test_one_course_row_has_totals_percentage_and_status(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] 3 of 4 attended -> one row ('CS101', name, 4, 3, 1, '75%', 'Good')."""
        statuses = ["present", "late", "absent", "present"]
        records = [att_rec("CS101", f"2026-10-0{i}", {ME: s}) for i, s in enumerate(statuses, 1)]
        make_dashboard().load_course_wise_attendance(records, courses)
        assert captured_tables[-1].rows == [("CS101", "Introduction to Programming", 4, 3, 1, "75%", "Good")]
        assert captured_tables[-1].tree == "cw_tree"

    @pytest.mark.boundary
    def test_74_percent_is_marked_low(self, make_dashboard, captured_tables, att_rec, courses):
        """[BVA] 37 of 50 = 74 % -> status 'Low' (75 % and above is 'Good')."""
        records = [att_rec("CS101", "2026-10-01", {ME: "present" if i < 37 else "absent"}) for i in range(50)]
        make_dashboard().load_course_wise_attendance(records, courses)
        assert captured_tables[-1].rows[0][5:] == ("74%", "Low")

    @pytest.mark.equivalence
    def test_two_courses_give_two_rows_in_order_of_first_record(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] Courses appear in the order their first record appears: CS202 then CS101."""
        records = [att_rec("CS202", "2026-10-01", {ME: "present"}), att_rec("CS101", "2026-10-01", {ME: "absent"})]
        make_dashboard().load_course_wise_attendance(records, courses)
        assert [row[0] for row in captured_tables[-1].rows] == ["CS202", "CS101"]

    @pytest.mark.equivalence
    def test_unknown_course_code_is_shown_as_unknown(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] A record whose course no longer exists gets the name 'Unknown'."""
        make_dashboard().load_course_wise_attendance([att_rec("CS999", "2026-10-01", {ME: "present"})], courses)
        assert captured_tables[-1].rows[0][:2] == ("CS999", "Unknown")

    @pytest.mark.equivalence
    def test_row_colour_tag_is_green_for_good_and_red_for_low(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] The tag function returns 'gA' for 'Good' rows and 'gF' for 'Low' rows."""
        make_dashboard().load_course_wise_attendance([att_rec("CS101", "2026-10-01", {ME: "present"})], courses)
        tag = captured_tables[-1].tag
        assert tag(("x", "x", 1, 1, 0, "100%", "Good")) == "gA"
        assert tag(("x", "x", 1, 0, 1, "0%", "Low")) == "gF"


class TestStudentDashboardClass:
    """Class-level behaviour: the filters and course list that build the student's screens."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    def test_attendance_log_lists_newest_first(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] 'All Courses' shows every record sorted by date, newest first."""
        from tests.conftest import FakeStore
        records = [att_rec("CS101", "2026-10-01", {ME: "present"}), att_rec("CS101", "2026-10-03", {ME: "absent"}),
                   att_rec("CS101", "2026-10-02", {ME: "late"})]
        dash = make_dashboard(store=FakeStore(attendanceRecords=records, courses=courses))
        dash.filter_attendance_log()
        assert [r[0] for r in captured_tables[-1].rows] == ["2026-10-03", "2026-10-02", "2026-10-01"]

    @pytest.mark.equivalence
    def test_attendance_log_can_be_filtered_by_course(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] Selecting 'CS202 - Data Structures' hides the CS101 records."""
        from tests.conftest import FakeStore
        records = [att_rec("CS101", "2026-10-01", {ME: "present"}), att_rec("CS202", "2026-10-02", {ME: "present"})]
        dash = make_dashboard(store=FakeStore(attendanceRecords=records, courses=courses),
                              att_filter="CS202 - Data Structures")
        dash.filter_attendance_log()
        assert captured_tables[-1].rows == [("2026-10-02", "CS202 - Data Structures", "Present")]

    @pytest.mark.equivalence
    def test_attendance_status_is_shown_with_a_capital_letter(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] Stored 'late' is displayed as 'Late'."""
        from tests.conftest import FakeStore
        dash = make_dashboard(store=FakeStore(attendanceRecords=[att_rec("CS101", "2026-10-01", {ME: "late"})],
                                              courses=courses))
        dash.filter_attendance_log()
        assert captured_tables[-1].rows[0][2] == "Late"

    @pytest.mark.equivalence
    def test_result_row_shows_type_marks_percentage_grade_and_date(self, make_dashboard, captured_tables, res_rec, courses):
        """[ECP] One approved midterm -> ('Midterm', 100, 85, '85.00%', 'A', '2026-10-02')."""
        from tests.conftest import FakeStore
        records = [res_rec("CS101", "midterm", 100, {ME: (85, "85.00", "A")})]
        dash = make_dashboard(store=FakeStore(resultsRecords=records), res_filter="CS101 - Introduction to Programming")
        dash.filter_course_results()
        assert captured_tables[-1].rows == [("Midterm", 100, 85, "85.00%", "A", "2026-10-02")]

    @pytest.mark.equivalence
    def test_my_courses_shows_the_attendance_percentage_per_course(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] 3 of 4 attended in CS101 -> the 'Attendance' column shows '75%'."""
        statuses = ["present", "late", "absent", "present"]
        records = [att_rec("CS101", f"2026-10-0{i}", {ME: s}) for i, s in enumerate(statuses, 1)]
        make_dashboard().load_my_courses([courses[0]], records)
        assert captured_tables[-1].rows == [("CS101", "Introduction to Programming", "Fatima Khan", "75%")]

    @pytest.mark.equivalence
    def test_my_courses_ignores_attendance_of_other_courses(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] Attendance records of CS202 do not change the percentage shown for CS101."""
        records = [att_rec("CS101", "2026-10-01", {ME: "present"}), att_rec("CS202", "2026-10-01", {ME: "absent"})]
        make_dashboard().load_my_courses([courses[0]], records)
        assert captured_tables[-1].rows[0][3] == "100%"
