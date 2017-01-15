import util.basic_util as b
import unittest

class TestClamp(unittest.TestCase):
    """A clamping function is usually simple enough that it shouldn't need testing, but it could be extended to different
     number types later."""
    def test_above(self):
        self.assertEqual(b.clamp(100,0,20),20)

    def test_below(self):
        self.assertEqual(b.clamp(-100,0,20),0)

    def test_in(self):
        self.assertEqual(b.clamp(10,0,20),10)

if __name__ == '__main__':
    unittest.main()
