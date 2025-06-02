#!/usr/bin/env python3
"""Test script to verify anita imports work correctly."""

# Test individual import
from anita.dating import utcnow

# Test package import
from anita import utcnow as utcnow_package

# Test that both work
if __name__ == "__main__":
    print("Direct import:", utcnow())
    print("Package import:", utcnow_package())
    print("Both imports work correctly!")
