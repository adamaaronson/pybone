from enum import Enum
from math import log2
import networkx as nx
from itertools import product
from dataclasses import dataclass
import argparse

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

ENHARMONICS = {
    'C#': Note.Db,
    'D#': Note.Eb,
    'E#': Note.F,
    'F#': Note.Gb,
    'G#': Note.Ab,
    'A#': Note.Bb,
    'B#': Note.C,
    'Cb': Note.B,
    'Fb': Note.E
}

SEMITONES_PER_OCTAVE = 12
A440_NOTE = Note.A
A440_OCTAVE = 4
A440_HERTZ = 440
A440_SEMITONES = A440_NOTE.value + SEMITONES_PER_OCTAVE * A440_OCTAVE
SPEED_OF_SOUND_MPS = 343

class Pitch:
    def __init__(self, note: Note, octave: int, offset: float = 0, name: str = None):
        self.note = note
        self.octave = octave
        self.offset = offset
        if name:
            self.name = name
        else:
            self.name = self.note.name

    def __hash__(self):
        return hash((self.name, self.note, self.octave, self.offset))

    def __repr__(self):
        if self.offset > 0:
            offset_text = '+{0:.3g}'.format(self.offset)
        elif self.offset < 0:
            offset_text = '{0:.3g}'.format(self.offset)
        else:
            offset_text = ''
        
        if self.name == 'B#':
            octave_text = str(self.octave - 1)
        elif self.name == 'Cb':
            octave_text = str(self.octave + 1)
        else:
            octave_text = str(self.octave)

        return self.name + octave_text + offset_text
    
    def __eq__(self, other):
        return self.note == other.note and self.octave == other.octave and self.offset == other.offset

    def get_semitones(self):
        semitones = self.note.value + self.octave * SEMITONES_PER_OCTAVE + self.offset
        return semitones - A440_SEMITONES
    
    @classmethod
    def from_string(cls, string: str):
        is_num = [c.isnumeric() for c in string]
        num_index = is_num.index(True)
        name = string[:num_index]

        if hasattr(Note, name):
            note = Note[name]
        elif name in ENHARMONICS:
            note = ENHARMONICS[name]
        
        octave = int(string[num_index:])
        if name == 'Cb':
            octave -= 1
        elif name == 'B#':
            octave += 1

        return Pitch(note, octave, name=name)

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
TROMBONE_SLIDE_LENGTH = 6.5
POSITIONS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th']
START_NODE = 'START'
END_NODE = 'END'

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
    
    def get_length(self, pitch: Pitch, partial: int):
        frequency = pitch.get_hertz() / (partial + 1)
        velocity = SPEED_OF_SOUND_MPS
        wavelength = velocity / frequency

        # length of tube is equal to half a wavelength
        # https://www.ww-p.org/common/pages/DisplayFile.aspx?itemId=13249884
        return wavelength * 0.5
    
    def get_slide_length(self, pitch: Pitch, partial: int):
        fundamental_length = self.get_length(self.fundamental, 0)
        pitch_length = self.get_length(pitch, partial)

        # slide has two sides, so divide by two
        return (pitch_length - fundamental_length) / 2

    @dataclass(frozen=True)
    class State:
        id: int
        pitch: Pitch
        position: float
        partial: int
        out: bool = False
    
    def get_states_of_pitch(self, id: int, pitch: Pitch, out=False):
        states = []
        
        positions, partials = self.get_positions_and_partials(pitch)
        for position, partial in zip(positions, partials):
            state = Trombone.State(id, pitch, position, partial, out)
            states.append(state)
        
        if not states:
            raise ValueError('pitch cannot be played: {}'.format(pitch))

        return states
    
    def get_states_of_pitches(self, pitches: list[Pitch], out=False):
        states = []
        for id, pitch in enumerate(pitches):
            states.append(self.get_states_of_pitch(id, pitch, out))
        return states
    
    def minimize_slide_movement(self, pitches: list[Pitch], round_positions=False):
        """
        Returns the list of slide positions that minimizes the amount
        of slide movement to play a given sequence of pitches.
        """

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
        path = path[1:-1] # remove start and end node
        
        if round_positions:
            path = [Trombone.State(t.id, t.pitch, round(t.position), t.partial) for t in path]
        
        return path
    
    def minimize_direction_changes(self, pitches: list[Pitch], round_positions=False):
        """
        Returns the list of slide positions that minimizes the
        number of slide direction changes.
        """

        in_states = self.get_states_of_pitches(pitches, out=False)
        out_states = self.get_states_of_pitches(pitches, out=True)

        DG = nx.DiGraph()
        DG.add_node(START_NODE)
        DG.add_node(END_NODE)

        for first_note_state in in_states[0]:
            DG.add_edge(START_NODE, first_note_state, weight=0)
        for first_note_state in out_states[0]:
            DG.add_edge(START_NODE, first_note_state, weight=0)
        
        for last_note_state in in_states[-1]:
            DG.add_edge(last_note_state, END_NODE, weight=0)
        for last_note_state in out_states[-1]:
            DG.add_edge(last_note_state, END_NODE, weight=0)
        
        for id in range(len(in_states) - 1):
            curr_in_states = in_states[id]
            curr_out_states = out_states[id]
            next_in_states = in_states[id + 1]
            next_out_states = out_states[id + 1]

            for curr_i, curr_state in enumerate(curr_in_states):
                for next_i, next_state in enumerate(next_in_states):
                    if curr_state.position > next_state.position: # position moves in
                        DG.add_edge(curr_in_states[curr_i], next_in_states[next_i], weight=0) # keep moving in
                        DG.add_edge(curr_out_states[curr_i], next_in_states[next_i], weight=1) # change direction from out to in
                    elif curr_state.position < next_state.position: # position moves out
                        DG.add_edge(curr_out_states[curr_i], next_out_states[next_i], weight=0) # keep moving out
                        DG.add_edge(curr_in_states[curr_i], next_out_states[next_i], weight=1) # change direction from in to out
                    else: # same position
                        DG.add_edge(curr_in_states[curr_i], next_in_states[next_i], weight=0) # does not change direction
                        DG.add_edge(curr_out_states[curr_i], next_out_states[next_i], weight=0) # does not change direction
        
        path = nx.shortest_path(DG, START_NODE, END_NODE, weight='weight')
        path = path[1:-1] # remove start and end node
        
        if round_positions:
            path = [Trombone.State(t.id, t.pitch, round(t.position), t.partial) for t in path]
        
        return path
    
    def minimize_partial_changes(self, pitches: list[Pitch], round_positions=False):
        """
        Returns the list of slide positions that minimizes the
        number of partial changes, to optimize for glissandos
        """
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

            for curr_state in curr_states:
                for next_state in next_states:
                    DG.add_edge(curr_state, next_state, weight=(0 if curr_state.partial == next_state.partial else 1))
        
        path = nx.shortest_path(DG, START_NODE, END_NODE, weight='weight')
        path = path[1:-1] # remove start and end node
        
        if round_positions:
            path = [Trombone.State(t.id, t.pitch, round(t.position), t.partial) for t in path]
        
        return path
    
    def maximize_partial_changes(self, pitches: list[Pitch], round_positions=False):
        """
        Returns the list of slide positions that minimizes the
        number of partial changes, to optimize for natural legato
        """
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

            for curr_state in curr_states:
                for next_state in next_states:
                    DG.add_edge(curr_state, next_state, weight=(1 if curr_state.partial == next_state.partial else 0))
        
        path = nx.shortest_path(DG, START_NODE, END_NODE, weight='weight')
        path = path[1:-1] # remove start and end node
        
        if round_positions:
            path = [Trombone.State(t.id, t.pitch, round(t.position), t.partial) for t in path]
        
        return path


def run(args):
    trombone = Trombone()
    pitches = [Pitch.from_string(note) for note in args.notes]

    if args.method == 'distance':
        states = trombone.minimize_slide_movement(pitches)
    elif args.method == 'direction':
        states = trombone.minimize_direction_changes(pitches)
    elif args.method == 'gliss':
        states = trombone.minimize_partial_changes(pitches)
    elif args.method == 'legato':
        states = trombone.maximize_partial_changes(pitches)
    else:
        raise ValueError('invalid method name: {}'.format(args.method))
    
    for state in states:
        print(state.pitch, Trombone.position_to_string(state.position), sep='\t')

def main():
    parser = argparse.ArgumentParser(description='pybone, the trombone optimizer')

    parser.add_argument('-m', '--method', dest='method', type=str,
                        default='distance', help='which method to use: distance, direction, gliss, legato')
    parser.add_argument('notes', metavar='notes', type=str, nargs='+',
                        help='note names')

    args = parser.parse_args()
    run(args)

if __name__ == '__main__':
    main()