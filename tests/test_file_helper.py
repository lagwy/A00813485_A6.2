"""
Unit tests for file_helper module.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

from file_helper import load_json_file  # noqa: E402


class TestLoadJsonFile(unittest.TestCase):
    """Tests for load_json_file."""

    def setUp(self):
        fd, self.filepath = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.filepath)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_returns_empty_list_when_file_missing(self):
        result = load_json_file(self.filepath)
        self.assertEqual(result, [])

    def test_returns_data_from_valid_file(self):
        data = [{"id": "1", "name": "Test"}]
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        result = load_json_file(self.filepath)
        self.assertEqual(result, data)

    def test_returns_empty_list_on_corrupt_json(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            fh.write("not valid json {{")
        result = load_json_file(self.filepath, error_label="customers")
        self.assertEqual(result, [])

    def test_corrupt_json_prints_error(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            fh.write("{bad json")
        with patch("builtins.print") as mock_print:
            result = load_json_file(self.filepath, error_label="reservations")
        self.assertEqual(result, [])
        mock_print.assert_called_once()
        self.assertIn("reservations", mock_print.call_args[0][0])

    def test_default_error_label(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            fh.write("bad json")
        result = load_json_file(self.filepath)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
