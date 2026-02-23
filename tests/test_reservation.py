"""
Unit tests for the Reservation class.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

from hotel import Hotel  # noqa: E402
from reservation import Reservation  # noqa: E402


class TestReservationInit(unittest.TestCase):
    """Tests for Reservation.__init__."""

    def test_attributes_set_correctly(self):
        res = Reservation("R1", "C1", "H1", 2, "2026-02-22")
        self.assertEqual(res.reservation_id, "R1")
        self.assertEqual(res.customer_id, "C1")
        self.assertEqual(res.hotel_id, "H1")
        self.assertEqual(res.room_count, 2)
        self.assertEqual(res.date, "2026-02-22")


class TestReservationToDict(unittest.TestCase):
    """Tests for Reservation.to_dict."""

    def test_to_dict_contains_all_fields(self):
        res = Reservation("R1", "C1", "H1", 2, "2026-02-22")
        data = res.to_dict()
        self.assertEqual(data["reservation_id"], "R1")
        self.assertEqual(data["customer_id"], "C1")
        self.assertEqual(data["hotel_id"], "H1")
        self.assertEqual(data["room_count"], 2)
        self.assertEqual(data["date"], "2026-02-22")


class TestReservationFromDict(unittest.TestCase):
    """Tests for Reservation.from_dict."""

    def test_from_dict_creates_reservation(self):
        data = {
            "reservation_id": "R1",
            "customer_id": "C1",
            "hotel_id": "H1",
            "room_count": 2,
            "date": "2026-02-22",
        }
        res = Reservation.from_dict(data)
        self.assertEqual(res.reservation_id, "R1")
        self.assertEqual(res.room_count, 2)

    def test_from_dict_missing_field_raises_key_error(self):
        with self.assertRaises(KeyError):
            Reservation.from_dict({"reservation_id": "R1"})


class TestReservationPrintReservation(unittest.TestCase):
    """Tests for Reservation.print_reservation."""

    def test_print_reservation_does_not_raise(self):
        res = Reservation("R1", "C1", "H1", 2, "2026-02-22")
        try:
            res.print_reservation()
        except Exception as exc:
            self.fail(f"print_reservation raised: {exc}")


class TestReservationPersistence(unittest.TestCase):
    """Tests for Reservation file persistence methods."""

    def setUp(self):
        fd, self.res_file = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.res_file)

        fd2, self.hotel_file = tempfile.mkstemp(suffix=".json")
        os.close(fd2)
        os.remove(self.hotel_file)

    def tearDown(self):
        for path in (self.res_file, self.hotel_file):
            if os.path.exists(path):
                os.remove(path)

    def _seed_hotel(self, hotel_id="H1", rooms=10):
        hotel = Hotel(hotel_id, "Fiesta Inn", "CDMX", rooms)
        Hotel.create_hotel(hotel, self.hotel_file)

    def _make_reservation(self, res_id="R1", customer_id="C1",
                          hotel_id="H1", rooms=2, date="2026-02-22"):
        return Reservation(res_id, customer_id, hotel_id, rooms, date)

    # create_reservation
    def test_create_reservation_success(self):
        self._seed_hotel(rooms=10)
        res = self._make_reservation()
        result = Reservation.create_reservation(
            res, self.res_file, self.hotel_file
        )
        self.assertTrue(result)
        reservations = Reservation._load_all(self.res_file)
        self.assertEqual(len(reservations), 1)
        self.assertEqual(reservations[0].reservation_id, "R1")

    def test_create_reservation_decrements_hotel_rooms(self):
        self._seed_hotel(rooms=10)
        res = self._make_reservation(rooms=3)
        Reservation.create_reservation(res, self.res_file, self.hotel_file)
        hotels = Hotel._load_all(self.hotel_file)
        self.assertEqual(hotels[0].available_rooms, 7)

    def test_create_reservation_fails_when_no_rooms(self):
        self._seed_hotel(rooms=1)
        res = self._make_reservation(rooms=5)
        result = Reservation.create_reservation(
            res, self.res_file, self.hotel_file
        )
        self.assertFalse(result)
        reservations = Reservation._load_all(self.res_file)
        self.assertEqual(len(reservations), 0)

    def test_create_reservation_fails_when_hotel_not_found(self):
        res = self._make_reservation(hotel_id="NONE")
        result = Reservation.create_reservation(
            res, self.res_file, self.hotel_file
        )
        self.assertFalse(result)

    # cancel_reservation
    def test_cancel_reservation_success(self):
        self._seed_hotel(rooms=10)
        res = self._make_reservation(rooms=3)
        Reservation.create_reservation(res, self.res_file, self.hotel_file)
        result = Reservation.cancel_reservation(
            "R1", self.res_file, self.hotel_file
        )
        self.assertTrue(result)
        reservations = Reservation._load_all(self.res_file)
        self.assertEqual(len(reservations), 0)

    def test_cancel_reservation_restores_hotel_rooms(self):
        self._seed_hotel(rooms=10)
        res = self._make_reservation(rooms=3)
        Reservation.create_reservation(res, self.res_file, self.hotel_file)
        Reservation.cancel_reservation("R1", self.res_file, self.hotel_file)
        hotels = Hotel._load_all(self.hotel_file)
        self.assertEqual(hotels[0].available_rooms, 10)

    def test_cancel_reservation_not_found(self):
        result = Reservation.cancel_reservation(
            "NONE", self.res_file, self.hotel_file
        )
        self.assertFalse(result)

    def test_create_multiple_then_cancel_one(self):
        self._seed_hotel(rooms=10)
        res1 = self._make_reservation("R1", rooms=2)
        res2 = self._make_reservation("R2", rooms=3)
        Reservation.create_reservation(res1, self.res_file, self.hotel_file)
        Reservation.create_reservation(res2, self.res_file, self.hotel_file)
        Reservation.cancel_reservation("R1", self.res_file, self.hotel_file)
        reservations = Reservation._load_all(self.res_file)
        self.assertEqual(len(reservations), 1)
        self.assertEqual(reservations[0].reservation_id, "R2")

    # error handling
    def test_load_all_corrupt_file_returns_empty(self):
        with open(self.res_file, "w", encoding="utf-8") as fh:
            fh.write("not valid json")
        reservations = Reservation._load_all(self.res_file)
        self.assertEqual(reservations, [])

    def test_load_all_invalid_record_skipped(self):
        with open(self.res_file, "w", encoding="utf-8") as fh:
            json.dump([{"bad": "data"}], fh)
        reservations = Reservation._load_all(self.res_file)
        self.assertEqual(reservations, [])

    def test_load_all_nonexistent_file_returns_empty(self):
        reservations = Reservation._load_all("/nonexistent/path/res.json")
        self.assertEqual(reservations, [])


if __name__ == "__main__":
    unittest.main()
