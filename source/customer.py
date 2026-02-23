"""
Customer

This module defines the Customer data class.
"""

import json
import os

CUSTOMERS_FILE = "customers.json"


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

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    @classmethod
    def _load_all(cls, filepath):
        """
        Load all customers from a JSON file.
        """
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as file_handle:
                raw = json.load(file_handle)
        except json.JSONDecodeError as exc:
            print(f"Error reading customers file '{filepath}': {exc}")
            return []

        customers = []
        for item in raw:
            try:
                customers.append(cls.from_dict(item))
            except KeyError as exc:
                print(
                    f"Error loading customer record (missing field {exc}): {item}"
                )
        return customers

    @staticmethod
    def _save_all(customers, filepath):
        """
        Save a list of Customer objects to a JSON file.
        """
        with open(filepath, "w", encoding="utf-8") as file_handle:
            json.dump([c.to_dict() for c in customers], file_handle, indent=2)

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    @classmethod
    def create_customer(cls, customer, filepath=CUSTOMERS_FILE):
        """
        Create a new customer in the file.
        """
        customers = cls._load_all(filepath)
        customers.append(customer)
        cls._save_all(customers, filepath)

    @classmethod
    def delete_customer(cls, customer_id, filepath=CUSTOMERS_FILE):
        """
        Remove a customer from the file by ID.

        """
        customers = cls._load_all(filepath)
        updated = [c for c in customers if c.customer_id != customer_id]
        if len(updated) == len(customers):
            print(f"Customer '{customer_id}' not found.")
        cls._save_all(updated, filepath)

    @classmethod
    def display_customer(cls, customer_id, filepath=CUSTOMERS_FILE):
        """
        Display information for a specific customer.
        """
        customers = cls._load_all(filepath)
        for customer in customers:
            if customer.customer_id == customer_id:
                customer.print_customer()
                return
        print(f"Customer '{customer_id}' not found.")

    @classmethod
    def modify_customer(cls, customer_id, updates, filepath=CUSTOMERS_FILE):
        """
        Modify an existing customer in the file.
        """
        customers = cls._load_all(filepath)
        found = False
        for customer in customers:
            if customer.customer_id == customer_id:
                for key, value in updates.items():
                    if hasattr(customer, key):
                        setattr(customer, key, value)
                    else:
                        print(f"Warning: Customer has no attribute '{key}'.")
                found = True
                break
        if not found:
            print(f"Customer '{customer_id}' not found.")
        cls._save_all(customers, filepath)
