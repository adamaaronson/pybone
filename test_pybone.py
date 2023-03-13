import unittest
from pybone import *

class TestGetHertz(unittest.TestCase):
    def runTest(self):
        self.assertAlmostEqual(Pitch(Note.A, 4).get_hertz(), 440.00, places=2)
        self.assertAlmostEqual(Pitch(Note.A, 5).get_hertz(), 880.00, places=2)
        self.assertAlmostEqual(Pitch(Note.A, 3).get_hertz(), 220.00, places=2)
        self.assertAlmostEqual(Pitch(Note.B, 4).get_hertz(), 493.88, places=2)
        self.assertAlmostEqual(Pitch(Note.C, 5).get_hertz(), 523.25, places=2)

class TestFromHertz(unittest.TestCase):
    def runTest(self):
        self.assertEqual(Pitch.from_hertz(440).remove_offset(), Pitch(Note.A, 4))
        self.assertEqual(Pitch.from_hertz(880).remove_offset(), Pitch(Note.A, 5))
        self.assertEqual(Pitch.from_hertz(220).remove_offset(), Pitch(Note.A, 3))
        self.assertEqual(Pitch.from_hertz(493).remove_offset(), Pitch(Note.B, 4))
        self.assertEqual(Pitch.from_hertz(523).remove_offset(), Pitch(Note.C, 5))

class TestGetPitchFirstPosition(unittest.TestCase):
    def runTest(self):
        trombone = Trombone()
        self.assertEqual(trombone.get_pitch(0, 0), Pitch(Note.Bb, 1))
        self.assertEqual(trombone.get_pitch(0, 1), Pitch(Note.Bb, 2))
        self.assertEqual(trombone.get_pitch(0, 2).remove_offset(), Pitch(Note.F, 3))
        self.assertEqual(trombone.get_pitch(0, 3), Pitch(Note.Bb, 3))
        self.assertEqual(trombone.get_pitch(0, 4).remove_offset(), Pitch(Note.D, 4))
        self.assertEqual(trombone.get_pitch(0, 5).remove_offset(), Pitch(Note.F, 4))

class TestGetPitchSecondPosition(unittest.TestCase):
    def runTest(self):
        trombone = Trombone()
        self.assertEqual(trombone.get_pitch(1, 0), Pitch(Note.A, 1))
        self.assertEqual(trombone.get_pitch(1, 1), Pitch(Note.A, 2))
        self.assertEqual(trombone.get_pitch(1, 2).remove_offset(), Pitch(Note.E, 3))
        self.assertEqual(trombone.get_pitch(1, 3), Pitch(Note.A, 3))
        self.assertEqual(trombone.get_pitch(1, 4).remove_offset(), Pitch(Note.Db, 4))
        self.assertEqual(trombone.get_pitch(1, 5).remove_offset(), Pitch(Note.E, 4))

class TestGetPitchSeventhPosition(unittest.TestCase):
    def runTest(self):
        trombone = Trombone()
        self.assertEqual(trombone.get_pitch(6, 0), Pitch(Note.E, 1))
        self.assertEqual(trombone.get_pitch(6, 1), Pitch(Note.E, 2))
        self.assertEqual(trombone.get_pitch(6, 2).remove_offset(), Pitch(Note.B, 2))
        self.assertEqual(trombone.get_pitch(6, 3), Pitch(Note.E, 3))
        self.assertEqual(trombone.get_pitch(6, 4).remove_offset(), Pitch(Note.Ab, 3))
        self.assertEqual(trombone.get_pitch(6, 5).remove_offset(), Pitch(Note.B, 3))

class TestGetPosition(unittest.TestCase):
    def runTest(self):
        trombone = Trombone()
        self.assertEqual(trombone.get_position(Pitch(Note.Bb, 2), 1), 0)
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.F, 3), 2), 0, places=1)
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.C, 3), 2), 5, places=1)

class TestAlternatePositions(unittest.TestCase):
    def runTest(self):
        trombone = Trombone()
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.D, 4), 4), 0, places=0)
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.D, 4), 5), 3, places=0)
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.F, 4), 5), 0, places=0)
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.F, 4), 6), 3, places=0)
        self.assertAlmostEqual(trombone.get_position(Pitch(Note.F, 4), 7), 5, places=0)

class TestGetAllPositions(unittest.TestCase):
    def runTest(self):
        trombone = Trombone()
        positions, partials = trombone.get_all_positions(Pitch(Note.D, 4))
        self.assertEqual(len(positions), 3)
        self.assertAlmostEqual(positions[0], 0, places=0)
        self.assertAlmostEqual(positions[1], 3, places=0)
        self.assertAlmostEqual(positions[2], 6, places=0)
        self.assertEqual(len(partials), 3)
        self.assertEqual(partials[0], 4)
        self.assertEqual(partials[1], 5)
        self.assertEqual(partials[2], 6)

class TestPositionToString(unittest.TestCase):
    def runTest(self):
        self.assertEqual(Trombone.position_to_string(0), 'First')
        self.assertEqual(Trombone.position_to_string(0.2), 'First+0.2')
        self.assertEqual(Trombone.position_to_string(-0.2), 'First-0.2')
        self.assertEqual(Trombone.position_to_string(5.2), 'Sixth+0.2')


if __name__ == '__main__':
    unittest.main()