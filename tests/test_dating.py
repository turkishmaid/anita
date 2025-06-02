"""Unit tests for the anita.dating module.

The unit tests successfully convert and expand upon the existing doctests
while providing comprehensive coverage for the entire dating module.
"""

import unittest
from datetime import datetime, date, timezone, UTC, timedelta
from unittest.mock import patch
import re

from anita.dating import (
    utcnow,
    sara_date,
    from_sara_date,
    split_seconds,
    check_date,
    number62,
    date62,
    datetime_from_date,
    utcage,
)


class TestUtcNow(unittest.TestCase):
    """Test cases for utcnow function."""

    def test_returns_timezone_aware_datetime(self):
        """Test that utcnow returns a timezone-aware datetime object."""
        result = utcnow()
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.tzinfo, UTC)

    def test_returns_current_time(self):
        """Test that utcnow returns current time (within a small tolerance)."""
        before = datetime.now(tz=UTC)
        result = utcnow()
        after = datetime.now(tz=UTC)

        self.assertLessEqual(before, result)
        self.assertLessEqual(result, after)


class TestSaraDate(unittest.TestCase):
    """Test cases for sara_date function."""

    def test_basic_date_string(self):
        """Test formatting a basic date string."""
        self.assertEqual(sara_date("2010-12-24"), "AC24")
        self.assertEqual(sara_date("2020-01-15"), "K115")
        self.assertEqual(sara_date("2021-09-30"), "L930")

    def test_datetime_string_with_time(self):
        """Test formatting a datetime string with time."""
        self.assertEqual(sara_date("2010-12-24T07:06"), "AC24-0706")
        self.assertEqual(sara_date("2020-01-15T23:59"), "K115-2359")
        self.assertEqual(sara_date("2021-09-30T00:00"), "L930-0000")

    def test_datetime_string_with_seconds(self):
        """Test formatting a datetime string with seconds (should be ignored)."""
        self.assertEqual(sara_date("2010-12-24T07:06:30"), "AC24-0706")
        self.assertEqual(sara_date("2020-01-15T23:59:59.999"), "K115-2359")

    def test_date_object(self):
        """Test formatting a date object."""
        test_date = date(2010, 12, 24)
        self.assertEqual(sara_date(test_date), "AC24")

        test_date = date(2020, 1, 15)
        self.assertEqual(sara_date(test_date), "K115")

    def test_datetime_object(self):
        """Test formatting a datetime object."""
        test_datetime = datetime(2010, 12, 24, 7, 6)
        self.assertEqual(sara_date(test_datetime), "AC24-0706")

        test_datetime = datetime(2020, 1, 15, 23, 59)
        self.assertEqual(sara_date(test_datetime), "K115-2359")

    def test_none_input_uses_current_time(self):
        """Test that None input uses current time."""
        with patch("anita.dating.utcnow") as mock_utcnow:
            mock_utcnow.return_value = datetime(2020, 5, 15, 10, 30, tzinfo=UTC)
            result = sara_date(None)
            self.assertEqual(result, "K515-1030")

    def test_year_before_2000_raises_assertion_error(self):
        """Test that years before 2000 raise an AssertionError."""
        with self.assertRaisesRegex(AssertionError, "Year must be >= 2000, got 1999"):
            sara_date("1999-12-31")

        with self.assertRaisesRegex(AssertionError, "Year must be >= 2000, got 1971"):
            sara_date(date(1971, 2, 24))

    def test_edge_cases_months(self):
        """Test edge cases for month encoding."""
        # Month 1 (January) -> "1"
        self.assertEqual(sara_date("2010-01-01"), "A101")
        # Month 9 (September) -> "9"
        self.assertEqual(sara_date("2010-09-01"), "A901")
        # Month 10 (October) -> "A"
        self.assertEqual(sara_date("2010-10-01"), "AA01")
        # Month 11 (November) -> "B"
        self.assertEqual(sara_date("2010-11-01"), "AB01")
        # Month 12 (December) -> "C"
        self.assertEqual(sara_date("2010-12-01"), "AC01")

    def test_edge_cases_years(self):
        """Test edge cases for year encoding."""
        # Year 2000 -> "0"
        self.assertEqual(sara_date("2000-01-01"), "0101")
        # Year 2009 -> "9"
        self.assertEqual(sara_date("2009-01-01"), "9101")
        # Year 2010 -> "A"
        self.assertEqual(sara_date("2010-01-01"), "A101")
        # Year 2035 -> "Z"
        self.assertEqual(sara_date("2035-01-01"), "Z101")


class TestFromSaraDate(unittest.TestCase):
    """Test cases for from_sara_date function."""

    def test_basic_conversion(self):
        """Test basic conversion from Sara date to date object."""
        result = from_sara_date("AC24")
        expected = date(2010, 12, 24)
        self.assertEqual(result, expected)

    def test_numeric_year_and_month(self):
        """Test conversion with numeric year and month."""
        result = from_sara_date("0101")
        expected = date(2000, 1, 1)
        self.assertEqual(result, expected)

        result = from_sara_date("9915")
        expected = date(2009, 9, 15)
        self.assertEqual(result, expected)

    def test_letter_month(self):
        """Test conversion with letter month (October-December)."""
        result = from_sara_date("AA01")  # 2010-10-01
        expected = date(2010, 10, 1)
        self.assertEqual(result, expected)

        result = from_sara_date("AB01")  # 2010-11-01
        expected = date(2010, 11, 1)
        self.assertEqual(result, expected)

        result = from_sara_date("AC01")  # 2010-12-01
        expected = date(2010, 12, 1)
        self.assertEqual(result, expected)

    def test_roundtrip_conversion(self):
        """Test that sara_date and from_sara_date are inverse operations."""
        original_dates = [
            date(2000, 1, 1),
            date(2010, 12, 24),
            date(2020, 6, 15),
            date(2035, 12, 31),
        ]

        for original_date in original_dates:
            sara = sara_date(original_date)
            converted_back = from_sara_date(sara)
            self.assertEqual(converted_back, original_date)


class TestSplitSeconds(unittest.TestCase):
    """Test cases for split_seconds function."""

    def test_only_seconds(self):
        """Test formatting when only seconds are present."""
        self.assertEqual(split_seconds(5.5), "5.5s")
        self.assertEqual(split_seconds(30.0), "30.0s")
        self.assertEqual(split_seconds(0.5), "0.5s")

    def test_minutes_and_seconds(self):
        """Test formatting with minutes and seconds."""
        self.assertEqual(split_seconds(65.5), "1m 5.5s")
        self.assertEqual(split_seconds(125.0), "2m 5.0s")

    def test_hours_minutes_seconds(self):
        """Test formatting with hours, minutes, and seconds."""
        self.assertEqual(split_seconds(3661.5), "1h 1m 1.5s")  # 1 hour, 1 minute, 1.5 seconds
        self.assertEqual(split_seconds(7200.0), "2h")  # exactly 2 hours

    def test_days_hours_minutes_seconds(self):
        """Test formatting with days, hours, minutes, and seconds."""
        self.assertEqual(split_seconds(90061.5), "1d 1h 1m 1.5s")  # 1 day, 1 hour, 1 minute, 1.5 seconds
        self.assertEqual(split_seconds(172800.0), "2d")  # exactly 2 days

    def test_edge_cases(self):
        """Test edge cases for split_seconds."""
        self.assertEqual(split_seconds(0.0), "no time")
        self.assertEqual(split_seconds(0.05), "no time")  # below 0.1 threshold
        self.assertEqual(split_seconds(0.1), "0.1s")
        self.assertEqual(split_seconds(60.0), "1m")  # exactly 1 minute
        self.assertEqual(split_seconds(3600.0), "1h")  # exactly 1 hour
        self.assertEqual(split_seconds(86400.0), "1d")  # exactly 1 day

    def test_large_values(self):
        """Test with large time values."""
        # 10 days, 5 hours, 30 minutes, 45.7 seconds
        large_seconds = 10 * 86400 + 5 * 3600 + 30 * 60 + 45.7
        self.assertEqual(split_seconds(large_seconds), "10d 5h 30m 45.7s")


class TestCheckDate(unittest.TestCase):
    """Test cases for check_date function."""

    def test_valid_dates(self):
        """Test valid date strings."""
        self.assertTrue(check_date("2023-01-01"))
        self.assertTrue(check_date("1999-12-31"))
        self.assertTrue(check_date("2000-02-29"))  # leap year
        self.assertTrue(check_date("2020-06-15"))

    def test_invalid_format(self):
        """Test invalid date formats."""
        self.assertFalse(check_date("23-01-01"))  # year too short
        self.assertFalse(check_date("2023-1-01"))  # month too short
        self.assertFalse(check_date("2023-01-1"))  # day too short
        self.assertFalse(check_date("2023/01/01"))  # wrong separator
        self.assertFalse(check_date("01-01-2023"))  # wrong order
        self.assertFalse(check_date("2023-13-01"))  # month out of range
        self.assertFalse(check_date("2023-01-32"))  # day out of range

    def test_invalid_century(self):
        """Test dates with invalid centuries."""
        self.assertFalse(check_date("1800-01-01"))  # 18th century
        self.assertFalse(check_date("3000-01-01"))  # 30th century
        self.assertFalse(check_date("0023-01-01"))  # ancient date

    def test_edge_cases(self):
        """Test edge cases."""
        self.assertFalse(check_date(""))
        self.assertFalse(check_date("not-a-date"))
        self.assertFalse(check_date("2023-01-01T10:30"))  # has time component


class TestNumber62(unittest.TestCase):
    """Test cases for number62 function."""

    def test_zero(self):
        """Test number62 with zero."""
        self.assertEqual(number62(0), "000")
        self.assertEqual(number62(0, pad=1), "0")
        self.assertEqual(number62(0, pad=5), "00000")

    def test_small_numbers(self):
        """Test number62 with small numbers."""
        self.assertEqual(number62(1), "001")
        self.assertEqual(number62(9), "009")
        self.assertEqual(number62(10), "00A")
        self.assertEqual(number62(35), "00Z")
        self.assertEqual(number62(36), "00a")
        self.assertEqual(number62(61), "00z")

    def test_larger_numbers(self):
        """Test number62 with larger numbers."""
        self.assertEqual(number62(62), "010")  # 1*62 + 0
        self.assertEqual(number62(124), "020")  # 2*62 + 0
        self.assertEqual(number62(3844), "100")  # 1*62^2 + 0*62 + 0

    def test_padding(self):
        """Test padding functionality."""
        self.assertEqual(number62(1, pad=1), "1")
        self.assertEqual(number62(1, pad=3), "001")
        self.assertEqual(number62(1, pad=5), "00001")
        self.assertEqual(number62(62, pad=2), "10")
        self.assertEqual(number62(62, pad=4), "0010")

    def test_base62_characters(self):
        """Test that all base62 characters are used correctly."""
        # Test the character mapping
        for i in range(62):
            result = number62(i, pad=1)
            expected_char = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"[i]
            self.assertEqual(result, expected_char)

    def test_strictly_ascending(self):
        """Test that the encoding is strictly ascending."""
        previous = ""
        for i in range(1000):
            current = number62(i)
            if previous:
                self.assertGreater(current, previous, f"number62({i}) = '{current}' should be > '{previous}'")
            previous = current


class TestDate62(unittest.TestCase):
    """Test cases for date62 function."""

    def test_epoch_date(self):
        """Test with the epoch date (1900-01-01)."""
        result = date62("1900-01-01")
        self.assertEqual(result, "000")

    def test_known_dates(self):
        """Test with some known dates."""
        # Jan 2, 1900 (day 1)
        self.assertEqual(date62("1900-01-02"), "001")

        # Dec 31, 1900 (day 364, since 1900 is not a leap year)
        self.assertEqual(date62("1900-12-31"), number62(364, pad=3))

    def test_modern_dates(self):
        """Test with modern dates."""
        # Test that it works with recent dates
        result = date62("2023-01-01")
        self.assertEqual(len(result), 3)
        self.assertTrue(all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" for c in result))

    def test_invalid_date_format(self):
        """Test that invalid date formats raise assertion error."""
        with self.assertRaises(AssertionError):
            date62("invalid-date")

        with self.assertRaises(AssertionError):
            date62("23-01-01")

    def test_strictly_ascending(self):
        """Test that date62 produces strictly ascending results for ascending dates."""
        dates = [
            "2020-01-01",
            "2020-01-02",
            "2020-02-01",
            "2020-12-31",
            "2021-01-01",
            "2023-06-15",
        ]

        previous = ""
        for date_str in dates:
            current = date62(date_str)
            if previous:
                self.assertGreater(current, previous, f"date62('{date_str}') = '{current}' should be > '{previous}'")
            previous = current


class TestDatetimeFromDate(unittest.TestCase):
    """Test cases for datetime_from_date function."""

    def test_date_object(self):
        """Test conversion from date object."""
        test_date = date(2023, 6, 15)
        result = datetime_from_date(test_date)
        expected = datetime(2023, 6, 15, 0, 0, 0)
        self.assertEqual(result, expected)

    def test_date_string(self):
        """Test conversion from date string."""
        result = datetime_from_date("2023-06-15")
        expected = datetime(2023, 6, 15, 0, 0, 0)
        self.assertEqual(result, expected)

    def test_different_dates(self):
        """Test with various dates."""
        test_cases = [
            ("2000-01-01", datetime(2000, 1, 1, 0, 0, 0)),
            ("2023-12-31", datetime(2023, 12, 31, 0, 0, 0)),
            ("2020-02-29", datetime(2020, 2, 29, 0, 0, 0)),  # leap year
        ]

        for date_str, expected in test_cases:
            result = datetime_from_date(date_str)
            self.assertEqual(result, expected)

    def test_assertion_on_invalid_type(self):
        """Test that invalid types raise assertion error."""
        with self.assertRaises(AssertionError):
            datetime_from_date(123)  # type: ignore[arg-type]

        with self.assertRaises(AssertionError):
            datetime_from_date(None)  # type: ignore[arg-type]


class TestUtcage(unittest.TestCase):
    """Test cases for utcage function."""

    def test_datetime_input(self):
        """Test with datetime input."""
        # Mock current time
        mock_now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        test_time = datetime(2023, 6, 15, 11, 59, 0, tzinfo=UTC)  # 1 minute ago

        with patch("anita.dating.utcnow", return_value=mock_now):
            result = utcage(test_time)
            self.assertEqual(result, 60)  # 60 seconds

    def test_timestamp_input(self):
        """Test with timestamp (float) input."""
        # Mock current time
        mock_now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        test_timestamp = mock_now.timestamp() - 120  # 2 minutes ago

        with patch("anita.dating.utcnow", return_value=mock_now):
            result = utcage(test_timestamp)
            self.assertEqual(result, 120)  # 120 seconds

    def test_timezone_handling(self):
        """Test that timezone-naive datetime is handled correctly."""
        mock_now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        test_time = datetime(2023, 6, 15, 11, 58, 0)  # timezone-naive, 2 minutes ago

        with patch("anita.dating.utcnow", return_value=mock_now):
            result = utcage(test_time)
            self.assertEqual(result, 120)  # 120 seconds

    def test_future_time(self):
        """Test with future time (negative age)."""
        mock_now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        test_time = datetime(2023, 6, 15, 12, 1, 0, tzinfo=UTC)  # 1 minute in future

        with patch("anita.dating.utcnow", return_value=mock_now):
            result = utcage(test_time)
            self.assertEqual(result, -60)  # -60 seconds

    def test_same_time(self):
        """Test with same time (zero age)."""
        mock_now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)

        with patch("anita.dating.utcnow", return_value=mock_now):
            result = utcage(mock_now)
            self.assertEqual(result, 0)

    def test_large_time_difference(self):
        """Test with large time differences."""
        mock_now = datetime(2023, 6, 15, 12, 0, 0, tzinfo=UTC)
        test_time = datetime(2023, 6, 14, 12, 0, 0, tzinfo=UTC)  # 1 day ago

        with patch("anita.dating.utcnow", return_value=mock_now):
            result = utcage(test_time)
            self.assertEqual(result, 86400)  # 24 * 60 * 60 seconds


if __name__ == "__main__":
    unittest.main()
