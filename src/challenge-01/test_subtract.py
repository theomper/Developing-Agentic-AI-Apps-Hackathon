import unittest
from subtract import subtract

class TestSubtract(unittest.TestCase):
    def test_subtract_positive_numbers(self):
        self.assertEqual(subtract(5, 3), 2)

    def test_subtract_negative_result(self):
        self.assertEqual(subtract(3, 5), -2)

    def test_subtract_zero(self):
        self.assertEqual(subtract(7, 0), 7)
        self.assertEqual(subtract(0, 7), -7)

    def test_subtract_negative_numbers(self):
        self.assertEqual(subtract(-3, -2), -1)
        self.assertEqual(subtract(-2, -3), 1)

if __name__ == "__main__":
    unittest.main()
