from enum import Enum
from math import log2

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

    def get_semitones(self) -> int:
        return self.value

SEMITONES_PER_OCTAVE = 12
A440_NOTE = Note.A
A440_OCTAVE = 4
A440_HERTZ = 440
A440_SEMITONES = A440_NOTE.get_semitones() + SEMITONES_PER_OCTAVE * A440_OCTAVE

class Pitch:
    def __init__(self, note: Note, octave: int):
        self.note = note
        self.octave = octave

    def __str__(self):
        return self.note.name + str(self.octave)
    
    def __eq__(self, other):
        return self.note == other.note and self.octave == other.octave

    def get_semitones(self):
        semitones = self.note.get_semitones() + self.octave * SEMITONES_PER_OCTAVE
        return semitones - A440_SEMITONES

    @classmethod
    def from_semitones(cls, semitones: float):
        note_semitones = round(semitones) + A440_SEMITONES
        note = Note(note_semitones % SEMITONES_PER_OCTAVE)
        octave = note_semitones // SEMITONES_PER_OCTAVE
        return cls(note, octave)
    
    def get_hertz(self):
        return A440_HERTZ * 2 ** (self.get_semitones() / SEMITONES_PER_OCTAVE)
    
    @classmethod
    def from_hertz(cls, hertz: float):
        semitones = log2(hertz / A440_HERTZ) * SEMITONES_PER_OCTAVE
        return cls.from_semitones(semitones)