#! /usr/bin/env python3

"""Unit tests for anita.jj module.

The unit tests are a significant enhancement over the doctests, providing
better test coverage, edge case handling, and maintainability.
The doctests serve more as documentation and basic functionality verification,
while the unit tests provide comprehensive testing suitable for a production
codebase.
"""

import json
import unittest
from datetime import UTC, date, datetime
from decimal import Decimal

from anita.jj import Accessor, dumps, jpath


class TestDumps(unittest.TestCase):
    """Test cases for the dumps function."""

    def test_simple_nested_dict_with_list(self) -> None:
        """Test basic nested structure with dict and list."""
        data = {"a": 1, "b": [2, 3], "c": {"d": 4}}
        expected = """{
    "a": 1,
    "b": [2, 3],
    "c": {"d": 4}
}"""
        self.assertEqual(dumps(data), expected)

    def test_nested_dict_with_multiple_values(self) -> None:
        """Test nested dict with multiple key-value pairs."""
        data = {"a": 1, "b": [2, 3], "c": {"d": 4, "e": 5}}
        expected = """{
    "a": 1,
    "b": [2, 3],
    "c": {"d": 4, "e": 5}
}"""
        self.assertEqual(dumps(data), expected)

    def test_deeply_nested_structure(self) -> None:
        """Test deeply nested structure requiring multiline formatting."""
        data = {"a": 1, "b": [2, 3], "c": {"d": 4, "e": [5, 6]}}
        expected = """{
    "a": 1,
    "b": [2, 3],
    "c": {
        "d": 4,
        "e": [5, 6]
    }
}"""
        self.assertEqual(dumps(data), expected)

    def test_atomic_values(self) -> None:
        """Test handling of atomic values."""
        self.assertEqual(dumps({"a": 1}), '{"a": 1}')
        self.assertEqual(dumps({"a": "hello"}), '{"a": "hello"}')
        self.assertEqual(dumps({"a": 3.14}), '{"a": 3.14}')
        self.assertEqual(dumps({"a": None}), '{"a": null}')

    def test_list_handling(self) -> None:
        """Test handling of different list types."""
        # Simple list
        self.assertEqual(dumps([1, 2, 3]), "[1, 2, 3]")

        # Nested list structure
        data = [{"a": 1}, {"b": 2}]
        expected = """[
    {"a": 1},
    {"b": 2}
]"""
        self.assertEqual(dumps(data), expected)

    def test_tuple_and_set_conversion(self) -> None:
        """Test that tuples and sets are converted to lists."""
        # Tuple converted to list
        self.assertEqual(dumps({"a": (1, 2, 3)}), '{\n    "a": [1, 2, 3]\n}')

        # Set converted to list (order may vary, so we check the structure)
        result = dumps({"a": {1, 2, 3}})
        # Parse the result to check it's a valid list
        parsed = json.loads(result)
        self.assertIsInstance(parsed["a"], list)
        self.assertEqual(set(parsed["a"]), {1, 2, 3})

    def test_datetime_and_decimal_support(self) -> None:
        """Test that datetime, date, and Decimal are converted to strings."""
        data = {
            "date": date(2023, 1, 1),
            "datetime": datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
            "decimal": Decimal("123.45"),
        }
        result = dumps(data)

        # Should contain string representations
        self.assertIn('"2023-01-01"', result)
        self.assertIn('"123.45"', result)

    def test_unsupported_type_raises_error(self) -> None:
        """Test that unsupported types raise TypeError."""

        class CustomClass:
            pass

        with self.assertRaises(TypeError):
            dumps({"a": CustomClass()})


class TestJpath(unittest.TestCase):
    """Test cases for the jpath function."""

    def setUp(self) -> None:
        """Set up test data."""
        self.test_data = {"data": [{"name": "Alice"}, {"name": "Bob"}]}

    def test_basic_jpath_access(self) -> None:
        """Test basic jpath access patterns."""
        self.assertEqual(jpath(self.test_data, "data/0/name"), "Alice")
        self.assertEqual(jpath(self.test_data, "data/1/name"), "Bob")

    def test_partial_path_access(self) -> None:
        """Test accessing partial paths."""
        expected = {"name": "Alice"}
        self.assertEqual(jpath(self.test_data, "data/0"), expected)

    def test_invalid_index_raises_error(self) -> None:
        """Test that invalid indices raise ValueError."""
        with self.assertRaises(ValueError) as cm:
            jpath(self.test_data, "data/2/name")

        self.assertIn("Invalid path '2/name'", str(cm.exception))
        self.assertIn("[{'name': 'Alice'}, {'name': 'Bob'}]", str(cm.exception))

    def test_invalid_key_for_list_raises_error(self) -> None:
        """Test that invalid keys for lists raise ValueError."""
        with self.assertRaises(ValueError) as cm:
            jpath(self.test_data, "data/name")

        self.assertIn("Invalid path 'name'", str(cm.exception))

    def test_indexing_string_raises_error(self) -> None:
        """Test that trying to index a string raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            jpath(self.test_data, "data/0/name/0")

        self.assertIn("Invalid path '0'", str(cm.exception))
        self.assertIn("'Alice'", str(cm.exception))

    def test_complex_nested_structure(self) -> None:
        """Test jpath with more complex nested structures."""
        complex_data = {
            "users": [
                {"id": 1, "profile": {"name": "Alice", "settings": {"theme": "dark"}}},
                {"id": 2, "profile": {"name": "Bob", "settings": {"theme": "light"}}},
            ],
        }

        self.assertEqual(jpath(complex_data, "users/0/profile/name"), "Alice")
        self.assertEqual(jpath(complex_data, "users/1/profile/settings/theme"), "light")

    def test_empty_path(self) -> None:
        """Test jpath with empty path."""
        with self.assertRaises(ValueError):
            jpath(self.test_data, "")


class TestAccessor(unittest.TestCase):
    """Test cases for the Accessor class."""

    def test_accessor_initialization_with_dict(self) -> None:
        """Test Accessor initialization with dict."""
        data = {"a": 1, "b": {"c": 2}}
        accessor = Accessor(data)
        self.assertEqual(accessor.a, 1)

    def test_accessor_initialization_with_list(self) -> None:
        """Test Accessor initialization with list."""
        data = [{"a": 1}, {"b": 2}]
        accessor = Accessor(data)
        self.assertEqual(accessor.jpath("0/a"), 1)

    def test_accessor_initialization_with_invalid_type(self) -> None:
        """Test that Accessor raises TypeError for invalid types."""
        with self.assertRaises(TypeError) as cm:
            Accessor(17)  # type: ignore[arg-type]

        self.assertIn("expected list or dict, got 'int'", str(cm.exception))

    def test_dot_notation_access(self) -> None:
        """Test dot notation access (one level only)."""
        data = {"a": 1, "b": {"c": 2}}
        accessor = Accessor(data)

        self.assertEqual(accessor.a, 1)
        # Note: This returns the raw dict, not wrapped in Accessor
        self.assertEqual(accessor.b, {"c": 2})

    def test_dot_notation_nonexistent_attribute(self) -> None:
        """Test that accessing nonexistent attribute raises AttributeError."""
        data = {"a": 1}
        accessor = Accessor(data)

        with self.assertRaises(AttributeError):
            _ = accessor.nonexistent

    def test_accessor_jpath_method(self) -> None:
        """Test jpath method of Accessor."""
        data = {"a": 1, "b": {"c": 2}}
        accessor = Accessor(data)

        self.assertEqual(accessor.jpath("b/c"), 2)

    def test_accessor_jpath_with_invalid_path(self) -> None:
        """Test jpath method with invalid path."""
        data = {"a": 1, "b": {"c": 2}}
        accessor = Accessor(data)

        with self.assertRaises(ValueError) as cm:
            accessor.jpath("b/0")

        self.assertIn("Invalid path '0'", str(cm.exception))
        self.assertIn("{'c': 2}", str(cm.exception))

    def test_accessor_with_list_data(self) -> None:
        """Test Accessor with list data using jpath."""
        data = [{"a": 1}, {"b": 2}]
        accessor = Accessor(data)

        self.assertEqual(accessor.jpath("0/a"), 1)
        self.assertEqual(accessor.jpath("1/b"), 2)

    def test_accessor_comprehensive_example(self) -> None:
        """Test comprehensive example matching the docstring."""
        obj = Accessor({"a": 1, "b": {"c": 2}})

        # Test dot notation
        self.assertEqual(obj.a, 1)

        # Test jpath
        self.assertEqual(obj.jpath("b/c"), 2)

        # Test that dot notation only works one level
        # (accessing obj.b.c would fail because obj.b returns a raw dict)
        b_value = obj.b
        self.assertEqual(b_value, {"c": 2})
        self.assertIsInstance(b_value, dict)  # Not wrapped in Accessor


if __name__ == "__main__":
    unittest.main()
