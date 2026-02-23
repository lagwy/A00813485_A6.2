"""
Reservation

This module defines the Reservation data class.
"""


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
