import unittest
from pybone import *

class TestGetHertz(unittest.TestCase):
    def runTest(self):
        self.assertAlmostEqual(Pitch(Note.A, 4).get_hertz(), 440, places=2)
        self.assertAlmostEqual(Pitch(Note.A, 5).get_hertz(), 880, places=2)
        self.assertAlmostEqual(Pitch(Note.A, 3).get_hertz(), 220, places=2)
        self.assertAlmostEqual(Pitch(Note.B, 4).get_hertz(), 493.88, places=2)
        self.assertAlmostEqual(Pitch(Note.C, 5).get_hertz(), 523.25, places=2)

class TestFromHertz(unittest.TestCase):
    def runTest(self):
        self.assertEqual(Pitch.from_hertz(440), Pitch(Note.A, 4))
        self.assertEqual(Pitch.from_hertz(880), Pitch(Note.A, 5))
        self.assertEqual(Pitch.from_hertz(220), Pitch(Note.A, 3))
        self.assertEqual(Pitch.from_hertz(493), Pitch(Note.B, 4))
        self.assertEqual(Pitch.from_hertz(523), Pitch(Note.C, 5))


if __name__ == '__main__':
    unittest.main()