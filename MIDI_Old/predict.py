#!/usr/bin/python3
import numpy as np
import keras, music21

from utility import *

length = 1000

seed = np.random.randint(0, len(X)-1)

pattern = X[seed]
pOut = []

print("\n")
for i in range(length):
	pIn = np.reshape(pattern, (1, len(pattern), 1)) / vocabSize

	prediction = model.predict(pIn, verbose=0)

	index = np.argmax(prediction)
	result = decoder[index]
	pOut.append(result)

	pattern = np.append(pattern, np.array(index))
	pattern = pattern[1:len(pattern)]

	print("\033[AGenerating note %d/%d." % (i+1, length))


# ============================================================================-

offset = 0
Y = []

print("Writing to 'output.mid'.")
for pitch, duration, off in pOut:
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
