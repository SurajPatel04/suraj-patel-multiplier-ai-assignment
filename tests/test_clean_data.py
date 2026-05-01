import sys
import pathlib
import pytest
import pandas as pd
import numpy as np

# Make the project root importable
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from clean_data import is_valid_email, parse_date_safe, normalize_status


# ─────────────────────────────────────────────
# TEST 1: is_valid_email
# ─────────────────────────────────────────────
class TestIsValidEmail:
    def test_valid_email(self):
        assert is_valid_email("user@example.com") is True

    def test_missing_at_symbol(self):
        assert is_valid_email("userexample.com") is False

    def test_missing_dot(self):
        assert is_valid_email("user@examplecom") is False

    def test_none_value(self):
        assert is_valid_email(None) is False

    def test_nan_value(self):
        assert is_valid_email(np.nan) is False

    def test_empty_string(self):
        assert is_valid_email("") is False

    def test_whitespace_only(self):
        assert is_valid_email("   ") is False


# ─────────────────────────────────────────────
# TEST 2: parse_date_safe
# ─────────────────────────────────────────────
class TestParseDateSafe:
    def test_yyyy_mm_dd(self):
        result = parse_date_safe("2024-01-15")
        assert result == pd.Timestamp("2024-01-15")

    def test_dd_mm_yyyy(self):
        result = parse_date_safe("15/01/2024")
        assert result == pd.Timestamp("2024-01-15")

    def test_mm_dd_yyyy(self):
        result = parse_date_safe("01-15-2024")
        assert result == pd.Timestamp("2024-01-15")

    def test_invalid_date_returns_nat(self):
        result = parse_date_safe("invalid-date")
        assert pd.isna(result)

    def test_none_returns_nat(self):
        result = parse_date_safe(None)
        assert pd.isna(result)


# ─────────────────────────────────────────────
# TEST 3: normalize_status
# ─────────────────────────────────────────────
class TestNormalizeStatus:
    def test_completed_variants(self):
        for val in ["completed", "Complete", "DONE", "done", "COMPLETED"]:
            assert normalize_status(val) == "completed", f"Failed for '{val}'"

    def test_pending_variants(self):
        for val in ["pending", "Pending", "PENDING", "In Progress", "waiting"]:
            assert normalize_status(val) == "pending", f"Failed for '{val}'"

    def test_cancelled_variants(self):
        for val in ["cancelled", "canceled", "Canceled", "CANCELLED", "cancel"]:
            assert normalize_status(val) == "cancelled", f"Failed for '{val}'"

    def test_refunded_variants(self):
        for val in ["refunded", "Refunded", "REFUNDED", "refund", "money back"]:
            assert normalize_status(val) == "refunded", f"Failed for '{val}'"

    def test_nan_input(self):
        result = normalize_status(np.nan)
        assert pd.isna(result)

    def test_unknown_status_returns_nan(self):
        result = normalize_status("gibberish")
        assert pd.isna(result)
