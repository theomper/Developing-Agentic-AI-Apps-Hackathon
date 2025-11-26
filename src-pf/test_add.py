"""
Tests for the add function
"""
import pytest
from add import add


def test_add_positive_numbers():
    """Test adding two positive numbers"""
    assert add(1, 2) == 3


def test_add_negative_numbers():
    """Test adding two negative numbers"""
    assert add(-1, -2) == -3


def test_add_positive_and_negative():
    """Test adding positive and negative numbers"""
    assert add(5, -3) == 2


def test_add_with_zero():
    """Test adding with zero"""
    assert add(0, 5) == 5
    assert add(5, 0) == 5


def test_add_decimal_numbers():
    """Test adding decimal numbers"""
    assert add(1.5, 2.5) == 4.0


def test_add_large_numbers():
    """Test adding large numbers"""
    assert add(1000000, 2000000) == 3000000
