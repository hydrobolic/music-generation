#!/usr/bin/python3
import numpy as np
import keras, music21

from utility import *

def nearest(q, l):
  return min(l, key=lambda x: abs(q - x))

length = 1000

seed = np.random.randint(0, len(notesX)-1)
# seed = 0

pattern = notesX[seed]
pOut = []

print("\n")
for i in range(length):
	pIn = np.reshape(pattern, (1, len(pattern), 1)) / noteVocabSize

	prediction = model.predict(pIn, verbose=0)

	index = np.argmax(prediction[0])
	pOut.append((
		noteDecoder[index],
		nearest(prediction[1][0][0], times),
		nearest(prediction[1][0][1], times)
	))

	pattern = np.append(pattern, np.array(index))
	pattern = pattern[1:len(pattern)]

	print("\033[AGenerating note %d/%d." % (i+1, length))


# =============================================================================

offset = 0
Y = []

print("Writing to 'output.mid'...")
for pitch, off, duration in pOut:
	cons = music21.chord.Chord if isinstance(pitch, tuple) else music21.note.Note
	
	n = cons(pitch)
	n.offset = offset
	n.quarterLength = duration
	n.storedInstrument = music21.instrument.Piano()
	Y.append(n)

	offset += off

	# print("\033[AWriting to MIDI %d/%d." % (i+1, length))

midi_stream = music21.stream.Stream(Y)
midi_stream.augmentOrDiminish(0.7, inPlace=True)
midi_stream.write("midi", fp="output.mid")


# =============================================================================


print("\nWriting to 'output.mp3'...")

import os
os.system("musescore output.mid -o output.mp3")
