"""
Reservation

This module defines the Reservation data class.
"""

import json

from hotel import Hotel
from file_helper import load_json_file

RESERVATIONS_FILE = "reservations.json"
RESERVATIONS_FILE_LABEL = "reservations"


class Reservation:
    """
    A room reservation linking a customer to a hotel.
    """

    def __init__(
        self,
        reservation_id,
        customer_id,
        hotel_id,
        room_count,
        date,
    ):
        """
        Initialize a Reservation instance.
        """
        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.hotel_id = hotel_id
        self.room_count = room_count
        self.date = date

    def to_dict(self):
        """
        Convert the reservation object to a dictionary.
        """
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "hotel_id": self.hotel_id,
            "room_count": self.room_count,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a reservation from a dictionary.
        """
        return cls(
            reservation_id=data["reservation_id"],
            customer_id=data["customer_id"],
            hotel_id=data["hotel_id"],
            room_count=data["room_count"],
            date=data["date"],
        )

    def print_reservation(self):
        """
        Print the reservation.
        """
        print(f"Reservation ID: {self.reservation_id}")
        print(f"Customer ID: {self.customer_id}")
        print(f"Hotel ID: {self.hotel_id}")
        print(f"Room Count: {self.room_count}")
        print(f"Date: {self.date}")

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    @classmethod
    def _load_all(cls, filepath):
        """
        Load all reservations from a JSON file.
        """
        raw = load_json_file(filepath, RESERVATIONS_FILE_LABEL)
        reservations = []
        for item in raw:
            try:
                reservations.append(cls.from_dict(item))
            except KeyError as exc:
                print(
                    f"Error loading reservation record "
                    f"(missing field {exc}): {item}"
                )
        return reservations

    @staticmethod
    def _save_all(reservations, filepath):
        """
        Save a list of Reservation objects to a JSON file.
        """
        with open(filepath, "w", encoding="utf-8") as file_handle:
            json.dump(
                [r.to_dict() for r in reservations], file_handle, indent=2
            )

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    @classmethod
    def create_reservation(
        cls,
        reservation,
        reservations_filepath=RESERVATIONS_FILE,
        hotels_filepath="hotels.json",
    ):
        """
        Create a new reservation and update hotel room availability.
        """
        success = Hotel.reserve_room(
            reservation.hotel_id,
            reservation.room_count,
            hotels_filepath,
        )
        if not success:
            return False
        reservations = cls._load_all(reservations_filepath)
        reservations.append(reservation)
        cls._save_all(reservations, reservations_filepath)
        return True

    @classmethod
    def cancel_reservation(
        cls,
        reservation_id,
        reservations_filepath=RESERVATIONS_FILE,
        hotels_filepath="hotels.json",
    ):
        """
        Cancel a reservation and restore hotel room availability.
        """
        reservations = cls._load_all(reservations_filepath)
        target = None
        for res in reservations:
            if res.reservation_id == reservation_id:
                target = res
                break

        if target is None:
            print(f"Reservation '{reservation_id}' not found.")
            return False

        Hotel.cancel_reservation(
            target.hotel_id,
            target.room_count,
            hotels_filepath,
        )
        updated = [
            r for r in reservations if r.reservation_id != reservation_id
        ]
        cls._save_all(updated, reservations_filepath)
        return True
