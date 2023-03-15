from enum import Enum
from math import log2
import networkx as nx
from itertools import product
from dataclasses import dataclass

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
    def __init__(self, note: Note, octave: int, offset: float = 0):
        self.note = note
        self.octave = octave
        self.offset = offset

    def __hash__(self):
        return hash((self.note, self.octave, self.offset))

    def __repr__(self):
        if self.offset > 0:
            offset_text = '+{0:.3g}'.format(self.offset)
        elif self.offset < 0:
            offset_text = '{0:.3g}'.format(self.offset)
        else:
            offset_text = ''
        return self.note.name + str(self.octave) + offset_text
    
    def __eq__(self, other):
        return self.note == other.note and self.octave == other.octave and self.offset == other.offset

    def get_semitones(self):
        semitones = self.note.get_semitones() + self.octave * SEMITONES_PER_OCTAVE + self.offset
        return semitones - A440_SEMITONES

    @classmethod
    def from_semitones(cls, semitones: float):
        note_semitones = semitones + A440_SEMITONES
        rounded_semitones = round(note_semitones)

        note = Note(rounded_semitones % SEMITONES_PER_OCTAVE)
        octave = rounded_semitones // SEMITONES_PER_OCTAVE
        offset = note_semitones - rounded_semitones
        return Pitch(note, octave, offset)
    
    def get_hertz(self):
        return A440_HERTZ * 2 ** (self.get_semitones() / SEMITONES_PER_OCTAVE)
    
    @classmethod
    def from_hertz(cls, hertz: float):
        semitones = log2(hertz / A440_HERTZ) * SEMITONES_PER_OCTAVE
        return Pitch.from_semitones(semitones)
    
    def remove_offset(self):
        return Pitch(self.note, self.octave)


TROMBONE_FUNDAMENTAL = Pitch(Note.Bb, 1)
TROMBONE_SLIDE_LENGTH = 7.5
POSITIONS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th']
START_NODE = 'START'
END_NODE = 'END'

@dataclass(frozen=True)
class TromboneState:
    id: int
    pitch: Pitch
    position: float
    partial: int

class Trombone:
    def __init__(self, fundamental: Pitch = TROMBONE_FUNDAMENTAL, slide_length: float = TROMBONE_SLIDE_LENGTH):
        self.fundamental = fundamental
        self.slide_length = slide_length
    
    @classmethod
    def position_to_string(cls, position: float):
        rounded_position = round(position)
        offset = position - rounded_position
        offset_prefix = '+' if offset > 0 else ''
        offset_text = '' if offset == 0 else '{0:.3g}'.format(offset)
        return '{}{}{}'.format(POSITIONS[rounded_position], offset_prefix, offset_text)
    
    def get_pitch(self, position: float, partial: int):
        """
        Returns the pitch played on a trombone in a given position and partial.
        Positions are 0-indexed, i.e. 0 is first position, 1 is second position, etc.
        Partials are 0-indexed from pedal, i.e. 0 is pedal Bb, 1 is Bb, 2 is F, etc.
        """
        semitones = self.fundamental.get_semitones() - position
        position_pitch = Pitch.from_semitones(semitones)
        position_pitch_hertz = position_pitch.get_hertz()
        position_partial_pitch_hertz = position_pitch_hertz * (partial + 1)
        position_partial_pitch = Pitch.from_hertz(position_partial_pitch_hertz)
        return position_partial_pitch
    
    def get_position(self, pitch: Pitch, partial: int):
        semitones = pitch.get_semitones()
        first_position_hertz = self.fundamental.get_hertz()
        first_position_partial_hertz = first_position_hertz * (partial + 1)
        first_position_partial_pitch = Pitch.from_hertz(first_position_partial_hertz)
        first_position_partial_semitones = first_position_partial_pitch.get_semitones()
        return first_position_partial_semitones - semitones
    
    def get_positions_and_partials(self, pitch: Pitch):
        positions = []
        partials = []
        partial = 0
        while True:
            position = self.get_position(pitch, partial)
            if position > self.slide_length:
                # partial is too high to play the note
                break
            if position > -0.5: # allow flat notes in first position
                positions.append(position)
                partials.append(partial)
            # otherwise, partial is too low to play the note yet
            partial += 1
        return positions, partials
    
    def get_states_of_pitch(self, id: int, pitch: Pitch):
        states = []
        
        positions, partials = self.get_positions_and_partials(pitch)
        for position, partial in zip(positions, partials):
            state = TromboneState(id, pitch, position, partial)
            states.append(state)

        return states
    
    def get_states_of_pitches(self, pitches: list[Pitch]):
        states = []
        for id, pitch in enumerate(pitches):
            states.append(self.get_states_of_pitch(id, pitch))
        return states
    
    def minimize_slide_movement(self, pitches: list[Pitch]):
        """
        Returns the list of slide positions that minimizes the amount
        of slide movement to play a given sequence of pitches.
        """

        if len(pitches) == 0:
            raise ValueError('pitches cannot be empty')

        states = self.get_states_of_pitches(pitches)

        DG = nx.DiGraph()
        DG.add_node(START_NODE)
        DG.add_node(END_NODE)

        for first_note_state in states[0]:
            DG.add_edge(START_NODE, first_note_state, weight=0)
        
        for last_note_state in states[-1]:
            DG.add_edge(last_note_state, END_NODE, weight=0)
        
        for id in range(len(states) - 1):
            curr_states = states[id]
            next_states = states[id + 1]
            state_pairs = [p for p in product(curr_states, next_states)]
            weighted_edges = [(u, v, abs(u.position - v.position)) for u, v in state_pairs]
            DG.add_weighted_edges_from(weighted_edges)
        
        path = nx.shortest_path(DG, START_NODE, END_NODE, weight='weight')
        return path[1:-1] # remove start and end node
        