"""
Hotel

This module defines the Hotel data class.
"""


class Hotel:
    """
    A hotel with rooms available for reservation.
    """

    def __init__(self, hotel_id, name, location, total_rooms):
        """
        Initialize a Hotel instance.
        """
        self.hotel_id = hotel_id
        self.name = name
        self.location = location
        self.total_rooms = total_rooms
        self.available_rooms = total_rooms

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
    def from_dict(data):
        """
        Create a hotel from a dictionary.
        """
        return Hotel(
            hotel_id=data["hotel_id"],
            name=data["name"],
            location=data["location"],
            total_rooms=data["total_rooms"],
            available_rooms=data["available_rooms"] if "available_rooms" in data else data["total_rooms"],
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
