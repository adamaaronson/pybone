from enum import Enum

SEMITONES_PER_OCTAVE = 12
A440_OCTAVE = 4
A440_HERTZ = 440

class Note(Enum):
    C = 0
    Db = 1
    D = 2
    Eb = 3
    E = 4
    F = 5
    Gb = 6
    G = 7
    Ab = 8
    A = 9
    Bb = 10
    B = 11

    def get_semitones(self):
        return self.value


class Pitch:   
    def __init__(self, note: Note, octave: int):
        self.note = note
        self.octave = octave

    def get_semitones(self):
        note_semitones = self.note.get_semitones() - Note.A.get_semitones()
        octave_semitones = (self.octave - A440_OCTAVE) * SEMITONES_PER_OCTAVE
        return note_semitones + octave_semitones
    
    def get_hertz(self):
        return A440_HERTZ * 2 ** (self.get_semitones() / SEMITONES_PER_OCTAVE)
    
    def __str__(self):
        return self.note.name + str(self.octave)


pitches = [
    Pitch(Note.A, 4),
    Pitch(Note.A, 5),
    Pitch(Note.A, 3),
    Pitch(Note.Bb, 4),
    Pitch(Note.Ab, 4),
]

for octave in range(5):
    for note in Note:
        p = Pitch(note, octave)
        print(p, p.get_hertz())