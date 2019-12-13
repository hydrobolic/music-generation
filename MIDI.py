#!/usr/bin/python
from __future__ import division
import mido, numpy as np
from scipy.io.wavfile import write
from itertools import chain
import os.path

# file = "afine-1.MID"
file = "AHouseis.mid"
path = os.path.join("data", file)

rate = 44100  # Sample rate
BPM  = 120    # Tempo

class memoize:
	def __init__(self, function):
		self.function = function
		self.cache = {}

	def __call__(self, *args):
		try: return self.cache[args]
		except KeyError:
			self.cache[args] = self.function(*args)
			return self.cache[args]

TWOPI = 2 * np.pi
ticks = rate/BPM
@memoize # Saves about 3/5 calls on AHouseis
def note(freq, length):
	steps = int(ticks * length)
	return np.sin(TWOPI * freq * np.linspace(0, steps - 1, steps)/rate)

def normalize(a): return (a - a.min()) / (np.ptp(a))
writeWAV = lambda a: write("%s.wav" % os.path.splitext(file)[0], rate, np.int16(32767 * normalize(a)).T)


# =============================================================================

midi = mido.MidiFile(path)
raw_notes = filter(lambda x: x.type == "note_on", max(midi.tracks, key=len)) # Read only the notes
data = map(lambda x: (int(440 * 2**((x.note-69)/12)), x.time), raw_notes)    # Convert MIDI numberings to frequencies
notes = np.hstack(np.array(map(lambda x: note(*x), data)))                   # Create notes as numpy arrays
writeWAV(notes)
