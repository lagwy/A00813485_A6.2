"""
Unit tests for the Hotel class.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

from hotel import Hotel  # noqa: E402


class TestHotelInit(unittest.TestCase):
    """Tests for Hotel.__init__."""

    def test_available_rooms_defaults_to_total(self):
        hotel = Hotel("H1", "Fiesta Inn", "CDMX", 100)
        self.assertEqual(hotel.available_rooms, 100)

    def test_custom_available_rooms(self):
        hotel = Hotel("H1", "Fiesta Inn", "CDMX", 100, available_rooms=80)
        self.assertEqual(hotel.available_rooms, 80)

    def test_attributes_set_correctly(self):
        hotel = Hotel("H2", "Holiday Inn", "Monterrey", 50)
        self.assertEqual(hotel.hotel_id, "H2")
        self.assertEqual(hotel.name, "Holiday Inn")
        self.assertEqual(hotel.location, "Monterrey")
        self.assertEqual(hotel.total_rooms, 50)


class TestHotelToDict(unittest.TestCase):
    """Tests for Hotel.to_dict."""

    def test_to_dict_contains_all_fields(self):
        hotel = Hotel("H1", "Fiesta Inn", "CDMX", 100, available_rooms=90)
        data = hotel.to_dict()
        self.assertEqual(data["hotel_id"], "H1")
        self.assertEqual(data["name"], "Fiesta Inn")
        self.assertEqual(data["location"], "CDMX")
        self.assertEqual(data["total_rooms"], 100)
        self.assertEqual(data["available_rooms"], 90)


class TestHotelFromDict(unittest.TestCase):
    """Tests for Hotel.from_dict."""

    def test_from_dict_with_available_rooms(self):
        data = {
            "hotel_id": "H1",
            "name": "Fiesta Inn",
            "location": "CDMX",
            "total_rooms": 100,
            "available_rooms": 90,
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.hotel_id, "H1")
        self.assertEqual(hotel.available_rooms, 90)

    def test_from_dict_defaults_available_to_total(self):
        data = {
            "hotel_id": "H1",
            "name": "Fiesta Inn",
            "location": "CDMX",
            "total_rooms": 100,
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.available_rooms, 100)

    def test_from_dict_missing_field_raises_key_error(self):
        with self.assertRaises(KeyError):
            Hotel.from_dict({"hotel_id": "H1"})


class TestHotelPrintHotel(unittest.TestCase):
    """Tests for Hotel.print_hotel."""

    def test_print_hotel_does_not_raise(self):
        hotel = Hotel("H1", "Fiesta Inn", "CDMX", 100)
        try:
            hotel.print_hotel()
        except Exception as exc:
            self.fail(f"print_hotel raised an exception: {exc}")


class TestHotelPersistence(unittest.TestCase):
    """Tests for Hotel file persistence methods."""

    def setUp(self):
        fd, self.filepath = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.filepath)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def _add_hotel(self, hotel_id="H1", name="Fiesta Inn", location="CDMX", rooms=100):
        hotel = Hotel(hotel_id, name, location, rooms)
        Hotel.create_hotel(hotel, self.filepath)
        return hotel

    # create_hotel
    def test_create_hotel_persists_to_file(self):
        self._add_hotel()
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(len(hotels), 1)
        self.assertEqual(hotels[0].hotel_id, "H1")

    def test_create_multiple_hotels(self):
        self._add_hotel("H1")
        self._add_hotel("H2", name="Holiday Inn")
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(len(hotels), 2)

    # delete_hotel
    def test_delete_existing_hotel(self):
        self._add_hotel()
        Hotel.delete_hotel("H1", self.filepath)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(len(hotels), 0)

    def test_delete_nonexistent_hotel_prints_message(self):
        self._add_hotel()
        Hotel.delete_hotel("NONE", self.filepath)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(len(hotels), 1)

    def test_delete_from_empty_file(self):
        Hotel.delete_hotel("H1", self.filepath)

    # display_hotel
    def test_display_existing_hotel_does_not_raise(self):
        self._add_hotel()
        try:
            Hotel.display_hotel("H1", self.filepath)
        except Exception as exc:
            self.fail(f"display_hotel raised: {exc}")

    def test_display_nonexistent_hotel_prints_message(self):
        Hotel.display_hotel("NONE", self.filepath)

    # modify_hotel
    def test_modify_hotel_updates_field(self):
        self._add_hotel()
        Hotel.modify_hotel("H1", {"name": "Updated"}, self.filepath)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].name, "Updated")

    def test_modify_hotel_invalid_attribute_prints_warning(self):
        self._add_hotel()
        Hotel.modify_hotel("H1", {"nonexistent": "val"}, self.filepath)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].hotel_id, "H1")

    def test_modify_nonexistent_hotel_prints_message(self):
        Hotel.modify_hotel("NONE", {"name": "X"}, self.filepath)

    # reserve_room
    def test_reserve_room_success(self):
        self._add_hotel(rooms=10)
        result = Hotel.reserve_room("H1", 3, self.filepath)
        self.assertTrue(result)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].available_rooms, 7)

    def test_reserve_room_not_enough_rooms(self):
        self._add_hotel(rooms=2)
        result = Hotel.reserve_room("H1", 5, self.filepath)
        self.assertFalse(result)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].available_rooms, 2)

    def test_reserve_room_exact_availability(self):
        self._add_hotel(rooms=5)
        result = Hotel.reserve_room("H1", 5, self.filepath)
        self.assertTrue(result)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].available_rooms, 0)

    def test_reserve_room_hotel_not_found(self):
        result = Hotel.reserve_room("NONE", 1, self.filepath)
        self.assertFalse(result)

    # cancel_reservation
    def test_cancel_reservation_restores_rooms(self):
        self._add_hotel(rooms=10)
        Hotel.reserve_room("H1", 3, self.filepath)
        result = Hotel.cancel_reservation("H1", 3, self.filepath)
        self.assertTrue(result)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].available_rooms, 10)

    def test_cancel_reservation_capped_at_total(self):
        self._add_hotel(rooms=10)
        result = Hotel.cancel_reservation("H1", 5, self.filepath)
        self.assertTrue(result)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels[0].available_rooms, 10)

    def test_cancel_reservation_hotel_not_found(self):
        result = Hotel.cancel_reservation("NONE", 1, self.filepath)
        self.assertFalse(result)

    # error handling
    def test_load_all_corrupt_file_returns_empty(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            fh.write("not valid json")
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels, [])

    def test_load_all_invalid_record_skipped(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump([{"bad": "data"}], fh)
        hotels = Hotel._load_all(self.filepath)
        self.assertEqual(hotels, [])

    def test_load_all_nonexistent_file_returns_empty(self):
        hotels = Hotel._load_all("/nonexistent/path/hotels.json")
        self.assertEqual(hotels, [])


if __name__ == "__main__":
    unittest.main()
