"""
Hotel

This module defines the Hotel data class.
"""

import json

from file_helper import load_json_file

HOTELS_FILE = "hotels.json"
HOTELS_FILE_LABEL = "hotels"


class Hotel:
    """
    A hotel with rooms available for reservation.
    """

    def __init__(
        self,
        hotel_id,
        name,
        location,
        total_rooms,
        available_rooms=None,
    ):
        """
        Initialize a Hotel instance.
        """
        self.hotel_id = hotel_id
        self.name = name
        self.location = location
        self.total_rooms = total_rooms
        self.available_rooms = (
            available_rooms if available_rooms is not None else total_rooms
        )

    def to_dict(self):
        """
        Convert the hotel object to a dictionary.
        """
        return {
            "hotel_id": self.hotel_id,
            "name": self.name,
            "location": self.location,
            "total_rooms": self.total_rooms,
            "available_rooms": self.available_rooms,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a hotel from a dictionary.
        """
        return cls(
            hotel_id=data["hotel_id"],
            name=data["name"],
            location=data["location"],
            total_rooms=data["total_rooms"],
            available_rooms=data.get("available_rooms", data["total_rooms"]),
        )

    def print_hotel(self):
        """
        Print the hotel.
        """
        print(f"Hotel ID: {self.hotel_id}")
        print(f"Name: {self.name}")
        print(f"Location: {self.location}")
        print(f"Total Rooms: {self.total_rooms}")
        print(f"Available Rooms: {self.available_rooms}")

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    @classmethod
    def _load_all(cls, filepath):
        """
        Load all hotels from a JSON file.
        """
        raw = load_json_file(filepath, HOTELS_FILE_LABEL)
        hotels = []
        for item in raw:
            try:
                hotels.append(cls.from_dict(item))
            except KeyError as exc:
                print(
                    f"Error loading hotel record "
                    f"(missing field {exc}): {item}"
                )
        return hotels

    @staticmethod
    def _save_all(hotels, filepath):
        """
        Save a list of Hotel objects to a JSON file.
        """
        with open(filepath, "w", encoding="utf-8") as file_handle:
            json.dump([h.to_dict() for h in hotels], file_handle, indent=2)

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    @classmethod
    def create_hotel(cls, hotel, filepath=HOTELS_FILE):
        """
        Create a new hotel in the file.
        """
        hotels = cls._load_all(filepath)
        hotels.append(hotel)
        cls._save_all(hotels, filepath)

    @classmethod
    def delete_hotel(cls, hotel_id, filepath=HOTELS_FILE):
        """
        Delete a hotel from the file by ID.
        """
        hotels = cls._load_all(filepath)
        updated = [h for h in hotels if h.hotel_id != hotel_id]
        if len(updated) == len(hotels):
            print(f"Hotel '{hotel_id}' not found.")
        cls._save_all(updated, filepath)

    @classmethod
    def display_hotel(cls, hotel_id, filepath=HOTELS_FILE):
        """
        Display information for a specific hotel.
        """
        hotels = cls._load_all(filepath)
        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                hotel.print_hotel()
                return
        print(f"Hotel '{hotel_id}' not found.")

    @classmethod
    def modify_hotel(cls, hotel_id, updates, filepath=HOTELS_FILE):
        """
        Modify an existing hotel in the file.
        """
        hotels = cls._load_all(filepath)
        found = False
        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                for key, value in updates.items():
                    if hasattr(hotel, key):
                        setattr(hotel, key, value)
                    else:
                        print(f"Warning: Hotel has no attribute '{key}'.")
                found = True
                break
        if not found:
            print(f"Hotel '{hotel_id}' not found.")
        cls._save_all(hotels, filepath)

    @classmethod
    def reserve_room(cls, hotel_id, room_count, filepath=HOTELS_FILE):
        """
        Reserve rooms for a hotel reservation.
        """
        hotels = cls._load_all(filepath)
        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                if hotel.available_rooms < room_count:
                    print(
                        f"Not enough available rooms in hotel '{hotel_id}'. "
                        f"Requested: {room_count}, "
                        f"Available: {hotel.available_rooms}"
                    )
                    return False
                hotel.available_rooms -= room_count
                cls._save_all(hotels, filepath)
                return True
        print(f"Hotel '{hotel_id}' not found.")
        return False

    @classmethod
    def cancel_reservation(cls, hotel_id, room_count, filepath=HOTELS_FILE):
        """
        Cancel a reservation and restore available rooms.
        """
        hotels = cls._load_all(filepath)
        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                hotel.available_rooms = min(
                    hotel.available_rooms + room_count, hotel.total_rooms
                )
                cls._save_all(hotels, filepath)
                return True
        print(f"Hotel '{hotel_id}' not found.")
        return False
