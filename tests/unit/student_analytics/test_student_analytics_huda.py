"""Module 3 - StudentDashboard calculations and table builders (class StudentDashboard).

Tests written by: Huda Asif (24F-3111)
Focus: empty data, other students' data, unknown values and hidden-data rules.
No Tk window is opened: tests/conftest.py builds the object with __new__ and replaces fill_table()
with a recorder, so the logic can be tested as a pure unit.
"""
import pytest

pytestmark = [pytest.mark.student_analytics, pytest.mark.huda]

ME = "2024-001"
OTHER = "2024-002"


class TestOverallAttendance:
    """Function under test: StudentDashboard.overall_attendance(records) -> (total, present, percent)."""

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.execution_order(1)
    def test_no_records_gives_zero_without_dividing_by_zero(self, make_dashboard):
        """[BVA] Empty list: (0, 0, 0) and no ZeroDivisionError."""
        assert make_dashboard().overall_attendance([]) == (0, 0, 0)

    @pytest.mark.negative
    def test_student_who_is_in_no_record_gets_zero(self, make_dashboard, att_rec):
        """[ECP-invalid] Records exist but none lists this student -> (0, 0, 0)."""
        records = [att_rec("CS101", "2026-10-01", {OTHER: "present"})]
        assert make_dashboard().overall_attendance(records) == (0, 0, 0)

    @pytest.mark.negative
    @pytest.mark.parametrize("status", ["excused", "PRESENT"])
    def test_unknown_status_counts_as_not_present(self, make_dashboard, att_rec, status):
        """[EG] Only the exact lowercase 'present' and 'late' count; anything else is an absence."""
        assert make_dashboard().overall_attendance([att_rec("CS101", "2026-10-01", {ME: status})]) == (1, 0, 0)

    @pytest.mark.negative
    def test_record_without_students_key_raises_key_error(self, make_dashboard):
        """[EG] Damaged record (no 'students' list) is not handled: KeyError."""
        with pytest.raises(KeyError):
            make_dashboard().overall_attendance([{"courseCode": "CS101", "date": "2026-10-01"}])

    @pytest.mark.negative
    def test_student_listed_twice_in_one_record_is_counted_once(self, make_dashboard):
        """[EG] Duplicate rows in one record: only the first matching row is used."""
        record = {"courseCode": "CS101", "date": "2026-10-01",
                  "students": [{"rollNo": ME, "status": "present"}, {"rollNo": ME, "status": "absent"}]}
        assert make_dashboard().overall_attendance([record]) == (1, 1, 100)


class TestAverageGrade:
    """Function under test: StudentDashboard.average_grade(records) -> (grade, count, average_percent)."""

    @pytest.mark.negative
    @pytest.mark.boundary
    def test_no_results_gives_dash_and_zero(self, make_dashboard):
        """[BVA] Empty list: grade '-', count 0, average 0."""
        assert make_dashboard().average_grade([]) == ("-", 0, 0)

    @pytest.mark.negative
    def test_results_of_other_students_only_gives_dash(self, make_dashboard, res_rec):
        """[ECP-invalid] Results exist but not for this student -> ('-', 0, 0)."""
        records = [res_rec("CS101", "midterm", 100, {OTHER: (90, "90.00", "A+")})]
        assert make_dashboard().average_grade(records) == ("-", 0, 0)

    @pytest.mark.negative
    def test_only_unapproved_results_gives_dash(self, make_dashboard, res_rec):
        """[ECP-invalid] Every result is unapproved -> nothing is counted."""
        records = [res_rec("CS101", "midterm", 100, {ME: (90, "90.00", "A+")}, approved=False)]
        assert make_dashboard().average_grade(records) == ("-", 0, 0)

    @pytest.mark.negative
    def test_non_numeric_percentage_text_raises_value_error(self, make_dashboard, res_rec):
        """[EG] Percentage is stored as text; 'abc' cannot be converted and raises ValueError."""
        records = [res_rec("CS101", "midterm", 100, {ME: (0, "abc", "-")})]
        with pytest.raises(ValueError):
            make_dashboard().average_grade(records)

    @pytest.mark.negative
    def test_average_is_a_plain_mean_not_weighted_by_total_marks(self, make_dashboard, res_rec):
        """[EG] 18/20 (90 %) and 40/100 (40 %) average to 65 %, not 46.7 %; grade B-."""
        records = [res_rec("CS101", "quiz", 20, {ME: (18, "90.00", "A")}),
                   res_rec("CS101", "final", 100, {ME: (40, "40.00", "F")})]
        assert make_dashboard().average_grade(records) == ("B-", 2, 65.0)


class TestLoadCourseWiseAttendance:
    """Function under test: StudentDashboard.load_course_wise_attendance(records, courses)."""

    @pytest.mark.negative
    @pytest.mark.boundary
    def test_no_records_shows_the_empty_message(self, make_dashboard, captured_tables, courses):
        """[BVA] Empty input -> no rows and the message 'No attendance records found'."""
        make_dashboard().load_course_wise_attendance([], courses)
        assert (captured_tables[-1].rows, captured_tables[-1].empty_msg) == ([], "No attendance records found")

    @pytest.mark.negative
    def test_other_students_records_are_not_shown(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP-invalid] A record of another student produces no row for this student."""
        make_dashboard().load_course_wise_attendance([att_rec("CS101", "2026-10-01", {OTHER: "present"})], courses)
        assert captured_tables[-1].rows == []

    @pytest.mark.equivalence
    def test_all_late_counts_as_fully_present(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] Two 'late' records -> 2 present, 0 absent, '100%', 'Good'."""
        records = [att_rec("CS101", "2026-10-01", {ME: "late"}), att_rec("CS101", "2026-10-02", {ME: "late"})]
        make_dashboard().load_course_wise_attendance(records, courses)
        assert captured_tables[-1].rows[0][2:] == (2, 2, 0, "100%", "Good")

    @pytest.mark.boundary
    def test_all_absent_is_zero_percent_and_low(self, make_dashboard, captured_tables, att_rec, courses):
        """[BVA] Lowest possible attendance: 0 of 2 -> '0%', 'Low'."""
        records = [att_rec("CS101", "2026-10-01", {ME: "absent"}), att_rec("CS101", "2026-10-02", {ME: "absent"})]
        make_dashboard().load_course_wise_attendance(records, courses)
        assert captured_tables[-1].rows[0][2:] == (2, 0, 2, "0%", "Low")

    @pytest.mark.equivalence
    def test_percentage_is_rounded_to_a_whole_number(self, make_dashboard, captured_tables, att_rec, courses):
        """[ECP] 2 of 3 attended = 66.67 % is displayed as '67%'."""
        records = [att_rec("CS101", "2026-10-01", {ME: "present"}), att_rec("CS101", "2026-10-02", {ME: "present"}),
                   att_rec("CS101", "2026-10-03", {ME: "absent"})]
        make_dashboard().load_course_wise_attendance(records, courses)
        assert captured_tables[-1].rows[0][5] == "67%"


class TestStudentDashboardClass:
    """Class-level behaviour: hidden-data rules and empty states of the filters."""

    @pytest.mark.negative
    @pytest.mark.smoke
    def test_results_without_a_selected_course_ask_the_user_to_choose(self, make_dashboard, captured_tables):
        """[BVA] No course selected -> empty table with 'Please select a course'."""
        from tests.conftest import FakeStore
        make_dashboard(store=FakeStore(resultsRecords=[]), res_filter="").filter_course_results()
        assert (captured_tables[-1].rows, captured_tables[-1].empty_msg) == ([], "Please select a course")

    @pytest.mark.negative
    def test_unapproved_results_are_hidden_from_the_student(self, make_dashboard, captured_tables, res_rec):
        """[ECP-invalid] approved=False results never reach the screen."""
        from tests.conftest import FakeStore
        records = [res_rec("CS101", "midterm", 100, {ME: (85, "85.00", "A")}, approved=False)]
        make_dashboard(store=FakeStore(resultsRecords=records), res_filter="CS101 - X").filter_course_results()
        assert captured_tables[-1].rows == []

    @pytest.mark.negative
    def test_results_of_other_students_are_hidden(self, make_dashboard, captured_tables, res_rec):
        """[ECP-invalid] Another student's marks are never shown; message 'No results found for this course'."""
        from tests.conftest import FakeStore
        records = [res_rec("CS101", "midterm", 100, {OTHER: (99, "99.00", "A+")})]
        make_dashboard(store=FakeStore(resultsRecords=records), res_filter="CS101 - X").filter_course_results()
        assert (captured_tables[-1].rows, captured_tables[-1].empty_msg) == ([], "No results found for this course")

    @pytest.mark.negative
    @pytest.mark.boundary
    def test_my_courses_with_no_courses_shows_the_empty_message(self, make_dashboard, captured_tables):
        """[BVA] Student enrolled in nothing -> no rows and 'No courses enrolled'."""
        make_dashboard().load_my_courses([], [])
        assert (captured_tables[-1].rows, captured_tables[-1].empty_msg) == ([], "No courses enrolled")

    @pytest.mark.boundary
    def test_course_without_any_classes_shows_zero_percent(self, make_dashboard, captured_tables, courses):
        """[BVA] Enrolled but no attendance yet -> '0%' (guarded against division by zero)."""
        make_dashboard().load_my_courses([courses[1]], [])
        assert captured_tables[-1].rows == [("CS202", "Data Structures", "Ahmed Hassan", "0%")]
