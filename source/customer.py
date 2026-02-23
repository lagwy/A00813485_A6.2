"""
Customer

This module defines the Customer data class.
"""


class Customer:
    """
     A customer of a hotel.
     """

    def __init__(self, customer_id, name, email):
        """
        Initialize a Customer instance.
        """
        self.customer_id = customer_id
        self.name = name
        self.email = email

    def to_dict(self):
        """
        Convert the customer object to a dictionary.
        """
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a customer from a dictionary.
        """
        return cls(
            customer_id=data["customer_id"],
            name=data["name"],
            email=data["email"],
        )

    def print_customer(self):
        """
        Print the customer.
        """
        print(f"Customer ID: {self.customer_id}")
        print(f"Name: {self.name}")
        print(f"Email: {self.email}")
