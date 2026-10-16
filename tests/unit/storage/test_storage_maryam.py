"""Module 2 - Storage class (data layer: get, set, log_activity, start-up behaviour).

Tests written by: Maryam Fatima (24F-3044)
Focus: normal behaviour (valid equivalence classes) and persistence.
Every test uses the isolated temp data file from tests/conftest.py, never the real portal_data.json.
"""
import json
import re

import pytest

import student_portal as sp

pytestmark = [pytest.mark.storage, pytest.mark.maryam]


def read_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class TestGet:
    """Function under test: Storage.get(key)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    @pytest.mark.execution_order(1)
    def test_existing_key_returns_the_stored_list(self, store):
        """[ECP] A key that exists returns its value (6 seeded users)."""
        assert len(store.get("systemUsers")) == 6

    @pytest.mark.equivalence
    def test_returns_the_same_object_not_a_copy(self, store):
        """[ECP] get() returns a reference, so changing the list changes the store."""
        users = store.get("systemUsers")
        users.append({"id": 99})
        assert store.data["systemUsers"][-1] == {"id": 99}

    @pytest.mark.equivalence
    def test_missing_key_returns_an_empty_list(self, store):
        """[ECP] A key that does not exist returns []."""
        assert store.get("doesNotExist") == []

    @pytest.mark.state
    def test_reading_a_missing_key_creates_it(self, store):
        """[ECP] Side effect of setdefault: after get() the new key exists in store.data."""
        store.get("newKey")
        assert store.data["newKey"] == []

    @pytest.mark.equivalence
    def test_non_list_value_is_returned_unchanged(self, store):
        """[ECP] get() is not limited to lists; the version string comes back as stored."""
        assert store.get("dataVersion") == sp.DATA_VERSION


class TestSet:
    """Function under test: Storage.set(key, value)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    def test_set_stores_the_value_in_memory(self, store):
        """[ECP] After set(), get() returns the same value."""
        store.set("courses", [{"code": "X1"}])
        assert store.get("courses") == [{"code": "X1"}]

    @pytest.mark.state
    def test_set_writes_to_the_file_immediately(self, store, isolated_data_file):
        """[ECP] The JSON file on disk already contains the value after set()."""
        store.set("note", "hello")
        assert read_file(isolated_data_file)["note"] == "hello"

    @pytest.mark.equivalence
    def test_set_overwrites_an_existing_key(self, store):
        """[ECP] A second set() on the same key replaces the first value."""
        store.set("courses", [1])
        store.set("courses", [2, 3])
        assert store.get("courses") == [2, 3]

    @pytest.mark.equivalence
    @pytest.mark.parametrize("value", [[1, 2], {"a": 1}])
    def test_set_accepts_every_json_type(self, store, value):
        """[ECP] list, dict, int, str, bool and float values are all stored and saved."""
        store.set("k", value)
        assert store.get("k") == value

    @pytest.mark.state
    def test_value_survives_an_application_restart(self, store):
        """[ECP] A new Storage object (a restart) loads the value from the file."""
        store.set("persisted", {"x": 1})
        assert sp.Storage().get("persisted") == {"x": 1}


class TestLogActivity:
    """Function under test: Storage.log_activity(action, user)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    def test_adds_exactly_one_entry_at_the_end(self, store):
        """[ECP] One call adds one entry (8 seeded -> 9), and it is the last one."""
        before = len(store.get("systemActivity"))
        store.log_activity("User Login", "Ali Ahmed")
        activity = store.get("systemActivity")
        assert len(activity) == before + 1
        assert (activity[-1]["action"], activity[-1]["user"]) == ("User Login", "Ali Ahmed")

    @pytest.mark.equivalence
    def test_entry_has_exactly_action_user_and_time(self, store):
        """[ECP] The stored entry contains the three expected keys and nothing else."""
        store.log_activity("Course Added", "Ali Ahmed")
        assert set(store.get("systemActivity")[-1]) == {"action", "user", "time"}

    @pytest.mark.equivalence
    def test_time_uses_the_yyyy_mm_dd_hh_mm_ss_format(self, store):
        """[ECP] The time text matches 'YYYY-MM-DD HH:MM:SS'."""
        store.log_activity("User Login", "Ali Ahmed")
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", store.get("systemActivity")[-1]["time"])

    @pytest.mark.state
    def test_entry_is_saved_to_the_file(self, store, isolated_data_file):
        """[ECP] log_activity() calls save(), so the file contains the new entry."""
        store.log_activity("Results Updated", "Fatima Khan")
        assert read_file(isolated_data_file)["systemActivity"][-1]["action"] == "Results Updated"

    @pytest.mark.state
    def test_entries_are_kept_in_call_order(self, store):
        """[ECP] Two calls give two entries in the same order they were made."""
        store.log_activity("first", "u1")
        store.log_activity("second", "u2")
        assert [a["action"] for a in store.get("systemActivity")[-2:]] == ["first", "second"]


class TestStorageClass:
    """Class-level behaviour: construction, seed data and reloading (Storage.__init__ + initialize_all_data)."""

    @pytest.mark.smoke
    @pytest.mark.equivalence
    @pytest.mark.execution_order(2)
    def test_fresh_start_seeds_users_courses_and_students(self, store):
        """[ECP] No file yet -> default data: 6 users, 3 courses, 3 students."""
        assert (len(store.get("systemUsers")), len(store.get("courses")), len(store.get("students"))) == (6, 3, 3)

    @pytest.mark.equivalence
    def test_fresh_start_seeds_attendance_results_and_activity(self, store):
        """[ECP] Default data also has 10 attendance records, 4 results and 8 activity entries."""
        assert (len(store.get("attendanceRecords")), len(store.get("resultsRecords")),
                len(store.get("systemActivity"))) == (10, 4, 8)

    @pytest.mark.equivalence
    def test_data_version_is_set(self, store):
        """[ECP] The data version marker equals DATA_VERSION."""
        assert store.data["dataVersion"] == sp.DATA_VERSION == "2.0"

    @pytest.mark.state
    def test_constructor_creates_the_data_file(self, isolated_data_file):
        """[ECP] Creating a Storage writes the file to disk."""
        assert not isolated_data_file.exists()
        sp.Storage()
        assert isolated_data_file.exists()

    @pytest.mark.state
    def test_restart_keeps_existing_data_and_does_not_reseed(self, store):
        """[ECP] Adding a user and restarting keeps 7 users (the seed data is not applied again)."""
        users = store.get("systemUsers")
        users.append({"id": 7, "name": "New User", "username": "new", "role": "student", "status": "active"})
        store.save()
        assert len(sp.Storage().get("systemUsers")) == 7
