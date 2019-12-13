import os, keras, pickle
import numpy as np
from music21 import converter, instrument, stream, note, chord

# times = [0, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 1, 3/2, 2, 3, 4, 8, 1/12, 1/6, 1/3, 2/3] # Non exhaustive list
# times = [0, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 1, 3/2, 2, 4, 8] # Non exhaustive list
# times = [0, 1/8, 1/4, 1/2, 3/4, 1, 3/2, 2, 4, 8] # Non exhaustive list
times = [1/4, 1/2, 1, 3/2, 2, 3, 4, 6, 8, 16] # Non exhaustive list

def nearest(q, l):
  return min(l, key=lambda x: abs(q - x))

weightsPath = "weights/weights.hdf5"
songsPath = "songs/input"
notesPath = "notesCache"
encodingPath = "encoder"

notes, offsets, durations = [], [], []
if os.access(notesPath, os.F_OK):
  with open(notesPath, "rb") as f:
    try: notes, offsets, durations = pickle.load(f)
    except EOFError: pass

if not notes:
  print("No notes to read from!")
  exit()

# # elements = sorted(set(item for item in notes), key=lambda x: x[0][0] if isinstance(x[0], tuple) else x[0])
# elements = \
#   list(sorted(set(n for n in notes if not isinstance(n[0], tuple)), key=lambda x: x[0])) + \
#   list(sorted(set(n for n in notes if     isinstance(n[0], tuple)), key=lambda x: x[0][0]))

with open(encodingPath, "rb") as f:
  elements = pickle.load(f)

noteEncoder = {n:i for i, n in enumerate(elements)}
noteDecoder = {i:n for i, n in enumerate(elements)}

noteVocabSize = len(elements)
print("noteVocabSize: %d" % noteVocabSize)

sequenceLength = 50


# =============================================================================

notesX = []
notesY = []
offsetDurationY = []

for i in range(len(notes) - sequenceLength):
  sequence_in = notes[i:i + sequenceLength]
  sequence_out = notes[i + sequenceLength]
  notesX.append([noteEncoder[char] for char in sequence_in])
  notesY.append(noteEncoder[sequence_out])
  offsetDurationY.append([offsets[i], durations[i]])

n = len(notesX)

notesX = np.reshape(notesX, (n, sequenceLength, 1)) / float(noteVocabSize)
notesY = keras.utils.np_utils.to_categorical(notesY)
offsetDurationY = np.array(offsetDurationY)


# =============================================================================

# model = keras.models.Sequential([
#   keras.layers.GRU(32, input_shape=(notesX.shape[1], notesX.shape[2])),
#   # keras.layers.Dropout(0.1),
#   keras.layers.Dense(noteVocabSize),
#   keras.layers.Activation("softmax"),
# ])

inputs = keras.layers.Input(shape=(notesX.shape[1], notesX.shape[2]))
layer1 = keras.layers.LSTM(32)(inputs)
classifier = keras.layers.Dense(noteVocabSize, activation="softmax", name="pitch")(layer1)
regression = keras.layers.Dense(2, activation="linear", name="offset/duration")(layer1)
model = keras.models.Model(inputs=inputs, outputs=[classifier, regression])

if os.access(weightsPath, os.F_OK):
  model.load_weights(weightsPath)

losses = {
  "pitch": "categorical_crossentropy",
  "offset/duration": "mean_squared_error"
}

model.compile(loss=losses, optimizer=keras.optimizers.RMSprop(lr=1e-2))
