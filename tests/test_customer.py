"""
Unit tests for the Customer class.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

from customer import Customer  # noqa: E402


class TestCustomerInit(unittest.TestCase):
    """Tests for Customer.__init__."""

    def test_attributes_set_correctly(self):
        customer = Customer("C1", "Luis", "luis@example.com")
        self.assertEqual(customer.customer_id, "C1")
        self.assertEqual(customer.name, "Luis")
        self.assertEqual(customer.email, "luis@example.com")


class TestCustomerToDict(unittest.TestCase):
    """Tests for Customer.to_dict."""

    def test_to_dict_contains_all_fields(self):
        customer = Customer("C1", "Luis", "luis@example.com")
        data = customer.to_dict()
        self.assertEqual(data["customer_id"], "C1")
        self.assertEqual(data["name"], "Luis")
        self.assertEqual(data["email"], "luis@example.com")


class TestCustomerFromDict(unittest.TestCase):
    """Tests for Customer.from_dict."""

    def test_from_dict_creates_customer(self):
        data = {
            "customer_id": "C1",
            "name": "Luis",
            "email": "luis@example.com",
        }
        customer = Customer.from_dict(data)
        self.assertEqual(customer.customer_id, "C1")
        self.assertEqual(customer.name, "Luis")
        self.assertEqual(customer.email, "luis@example.com")

    def test_from_dict_missing_field_raises_key_error(self):
        with self.assertRaises(KeyError):
            Customer.from_dict({"customer_id": "C1"})


class TestCustomerPrintCustomer(unittest.TestCase):
    """Tests for Customer.print_customer."""

    def test_print_customer_does_not_raise(self):
        customer = Customer("C1", "Luis", "luis@example.com")
        try:
            customer.print_customer()
        except Exception as exc:
            self.fail(f"print_customer raised: {exc}")


class TestCustomerPersistence(unittest.TestCase):
    """Tests for Customer file persistence methods."""

    def setUp(self):
        fd, self.filepath = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.filepath)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def _add_customer(
        self,
        customer_id="C1",
        name="Luis",
        email="luis@example.com",
    ):
        customer = Customer(customer_id, name, email)
        Customer.create_customer(customer, self.filepath)
        return customer

    # create_customer
    def test_create_customer_persists_to_file(self):
        self._add_customer()
        customers = Customer._load_all(self.filepath)
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].customer_id, "C1")

    def test_create_multiple_customers(self):
        self._add_customer("C1")
        self._add_customer("C2", name="Luis", email="luis@example.com")
        customers = Customer._load_all(self.filepath)
        self.assertEqual(len(customers), 2)

    # delete_customer
    def test_delete_existing_customer(self):
        self._add_customer()
        Customer.delete_customer("C1", self.filepath)
        customers = Customer._load_all(self.filepath)
        self.assertEqual(len(customers), 0)

    def test_delete_nonexistent_customer_prints_message(self):
        self._add_customer()
        Customer.delete_customer("NONE", self.filepath)
        customers = Customer._load_all(self.filepath)
        self.assertEqual(len(customers), 1)

    def test_delete_from_empty_file(self):
        Customer.delete_customer("C1", self.filepath)

    # display_customer
    def test_display_existing_customer_does_not_raise(self):
        self._add_customer()
        try:
            Customer.display_customer("C1", self.filepath)
        except Exception as exc:
            self.fail(f"display_customer raised: {exc}")

    def test_display_nonexistent_customer_prints_message(self):
        Customer.display_customer("NONE", self.filepath)

    # modify_customer
    def test_modify_customer_updates_field(self):
        self._add_customer()
        Customer.modify_customer(
            "C1", {"name": "Luis Updated"}, self.filepath
        )
        customers = Customer._load_all(self.filepath)
        self.assertEqual(customers[0].name, "Luis Updated")

    def test_modify_customer_updates_email(self):
        self._add_customer()
        Customer.modify_customer(
            "C1", {"email": "luis@example.com"}, self.filepath
        )
        customers = Customer._load_all(self.filepath)
        self.assertEqual(customers[0].email, "luis@example.com")

    def test_modify_customer_invalid_attribute_prints_warning(self):
        self._add_customer()
        Customer.modify_customer("C1", {"nonexistent": "val"}, self.filepath)
        customers = Customer._load_all(self.filepath)
        self.assertEqual(customers[0].customer_id, "C1")

    def test_modify_nonexistent_customer_prints_message(self):
        Customer.modify_customer("NONE", {"name": "X"}, self.filepath)

    # error handling
    def test_load_all_corrupt_file_returns_empty(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            fh.write("not valid json")
        customers = Customer._load_all(self.filepath)
        self.assertEqual(customers, [])

    def test_load_all_invalid_record_skipped(self):
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump([{"bad": "data"}], fh)
        customers = Customer._load_all(self.filepath)
        self.assertEqual(customers, [])

    def test_load_all_nonexistent_file_returns_empty(self):
        customers = Customer._load_all("/nonexistent/path/customers.json")
        self.assertEqual(customers, [])


if __name__ == "__main__":
    unittest.main()
