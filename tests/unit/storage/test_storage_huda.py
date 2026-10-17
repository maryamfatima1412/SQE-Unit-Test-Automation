"""Module 2 - Storage class (data layer: get, set, log_activity, start-up behaviour).

Tests written by: Huda Asif (24F-3111)
Focus: invalid / unusual input, error handling and damaged or old data files.
Every test uses the isolated temp data file from tests/conftest.py, never the real portal_data.json.
"""
import json

import pytest

import student_portal as sp

pytestmark = [pytest.mark.storage, pytest.mark.huda]


def read_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class TestGet:
    """Function under test: Storage.get(key)."""

    @pytest.mark.negative
    def test_empty_string_key_returns_an_empty_list(self, store):
        """[BVA] Shortest possible key (empty string) works and creates an empty list."""
        assert store.get("") == []
        assert "" in store.data

    @pytest.mark.equivalence
    def test_unicode_key_is_supported(self, store):
        """[EG] Keys in Urdu script are valid dictionary keys."""
        assert store.get("طلبہ") == []

    @pytest.mark.state
    def test_get_does_not_write_the_file(self, store, isolated_data_file):
        """[EG] The key created by get() exists only in memory until save() is called."""
        store.get("memoryOnly")
        assert "memoryOnly" not in read_file(isolated_data_file)

    @pytest.mark.state
    def test_get_returns_what_set_stored(self, store):
        """[EG] set() followed by get() returns the identical object."""
        value = {"a": [1, 2, 3]}
        store.set("k", value)
        assert store.get("k") is value

    @pytest.mark.state
    def test_changes_made_through_get_are_saved_only_after_save(self, store, isolated_data_file):
        """[EG] Editing the list from get() is lost on restart unless save() is called."""
        store.get("courses").append({"code": "NEW"})
        assert all(c["code"] != "NEW" for c in read_file(isolated_data_file)["courses"])
        store.save()
        assert any(c["code"] == "NEW" for c in read_file(isolated_data_file)["courses"])


class TestSet:
    """Function under test: Storage.set(key, value)."""

    @pytest.mark.negative
    def test_none_value_is_stored_and_returned_by_get(self, store):
        """[EG] None is a valid JSON null; get() returns None because the key exists."""
        store.set("k", None)
        assert store.get("k") is None

    @pytest.mark.negative
    def test_value_that_is_not_json_serialisable_raises_type_error(self, store):
        """[ECP-invalid] A Python set cannot be written as JSON, so TypeError is raised."""
        with pytest.raises(TypeError):
            store.set("bad", {1, 2, 3})

    @pytest.mark.negative
    @pytest.mark.state
    def test_failed_save_leaves_memory_and_disk_different(self, store, isolated_data_file):
        """[EG] set() changes memory first: after the TypeError the bad value is still in memory."""
        with pytest.raises(TypeError):
            store.set("bad", {1, 2})
        assert store.data["bad"] == {1, 2}

    @pytest.mark.equivalence
    def test_urdu_text_round_trips_through_the_file(self, store):
        """[EG] Non-ASCII text survives set() -> restart -> get()."""
        store.set("name", "فاطمہ خان")
        assert sp.Storage().get("name") == "فاطمہ خان"

    @pytest.mark.negative
    def test_unwritable_location_prints_a_message_and_does_not_crash(self, store, monkeypatch, tmp_path, capsys):
        """[EG] If the file cannot be written, save() reports it on screen but set() still works in memory."""
        monkeypatch.setattr(sp, "DATA_FILE", str(tmp_path / "missing_folder" / "data.json"))
        store.set("k", 1)
        assert "Could not save data" in capsys.readouterr().out
        assert store.get("k") == 1


class TestLogActivity:
    """Function under test: Storage.log_activity(action, user)."""

    @pytest.mark.negative
    def test_empty_action_and_user_are_accepted(self, store):
        """[BVA] No validation: empty strings are logged as they are."""
        store.log_activity("", "")
        assert store.get("systemActivity")[-1]["action"] == ""
        assert store.get("systemActivity")[-1]["user"] == ""

    @pytest.mark.negative
    def test_creates_the_activity_list_when_it_is_missing(self, store):
        """[EG] If 'systemActivity' was deleted, the first log_activity() recreates it."""
        del store.data["systemActivity"]
        store.log_activity("User Login", "Ali Ahmed")
        assert len(store.data["systemActivity"]) == 1

    @pytest.mark.equivalence
    def test_unicode_user_name_is_logged(self, store):
        """[EG] A user name written in Urdu is stored and reloaded correctly."""
        store.log_activity("User Login", "فاطمہ خان")
        assert sp.Storage().get("systemActivity")[-1]["user"] == "فاطمہ خان"

    @pytest.mark.boundary
    def test_log_has_no_size_limit(self, store):
        """[BVA] 100 more entries are all kept: 8 seeded + 100 = 108 (the log grows forever)."""
        for i in range(100):
            store.log_activity("tick", str(i))
        assert len(store.get("systemActivity")) == 108

    @pytest.mark.state
    def test_time_comes_from_the_current_clock(self, store, frozen_now):
        """[EG] With the clock frozen at 2026-10-15 12:00:00 the entry carries exactly that time."""
        store.log_activity("User Login", "Ali Ahmed")
        assert store.get("systemActivity")[-1]["time"] == "2026-10-15 12:00:00"


class TestStorageClass:
    """Class-level behaviour with damaged, empty or old data files."""

    @pytest.mark.negative
    @pytest.mark.execution_order(1)
    def test_corrupt_json_file_is_replaced_by_seed_data(self, isolated_data_file):
        """[EG] Invalid JSON does not crash; the app starts with the default data (data is lost silently)."""
        isolated_data_file.write_text("{ this is not valid json", encoding="utf-8")
        assert len(sp.Storage().get("systemUsers")) == 6

    @pytest.mark.negative
    def test_empty_file_is_treated_like_a_missing_file(self, isolated_data_file):
        """[BVA] A zero-byte file raises a JSON error internally and leads to the seed data."""
        isolated_data_file.write_text("", encoding="utf-8")
        assert len(sp.Storage().get("courses")) == 3

    @pytest.mark.state
    def test_old_data_version_wipes_all_custom_data(self, isolated_data_file):
        """[EG] A file with another dataVersion is cleared completely, including keys the app does not know."""
        isolated_data_file.write_text(json.dumps({"dataVersion": "1.0", "customKey": [1, 2, 3]}), encoding="utf-8")
        s = sp.Storage()
        assert "customKey" not in s.data
        assert s.data["dataVersion"] == "2.0"

    @pytest.mark.state
    def test_missing_table_is_added_but_existing_tables_are_not_touched(self, isolated_data_file):
        """[ECP] Current version, only one custom user table -> users kept, the other tables are created."""
        only_user = [{"id": 1, "name": "Only", "username": "only", "role": "admin", "status": "active"}]
        isolated_data_file.write_text(json.dumps({"dataVersion": "2.0", "systemUsers": only_user}), encoding="utf-8")
        s = sp.Storage()
        assert s.get("systemUsers") == only_user
        assert len(s.get("courses")) == 3

    @pytest.mark.state
    def test_initialize_all_data_is_idempotent(self, store):
        """[EG] Calling initialize_all_data() again changes nothing (seed data is created only once)."""
        before = json.dumps(store.data, sort_keys=True)
        store.initialize_all_data()
        assert json.dumps(store.data, sort_keys=True) == before
