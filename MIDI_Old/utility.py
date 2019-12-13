import os, keras, pickle
import numpy as np
from music21 import converter, instrument, stream, note, chord

weightsPath = "weights/weights.hdf5"
songsPath = "songs/input"
notesPath = "notesCache"
encodingPath = "encoder"

immutableNotes = []
if os.access(notesPath, os.F_OK):
  with open(notesPath, "rb") as f:
    try: immutableNotes = pickle.load(f)
    except EOFError: pass

if not immutableNotes:
  print("No notes to read from!")
  exit()

# # elements = sorted(set(item for item in immutableNotes), key=lambda x: x[0][0] if isinstance(x[0], tuple) else x[0])
# elements = \
#   list(sorted(set(n for n in immutableNotes if not isinstance(n[0], tuple)), key=lambda x: x[0])) + \
#   list(sorted(set(n for n in immutableNotes if     isinstance(n[0], tuple)), key=lambda x: x[0][0]))

with open(encodingPath, "rb") as f: elements = pickle.load(f)

encoder = {n:i for i, n in enumerate(elements)}
decoder = {i:n for i, n in enumerate(elements)}

vocabSize = len(set(note for note in immutableNotes))
print("vocabSize: %d" % vocabSize)

sequenceLength = 50
print(elements)


# =============================================================================

X, Y = [], []

for i in range(len(immutableNotes) - sequenceLength):
  sequence_in = immutableNotes[i:i + sequenceLength]
  sequence_out = immutableNotes[i + sequenceLength]
  X.append([encoder[char] for char in sequence_in])
  Y.append(encoder[sequence_out])

n = len(X)

X = np.reshape(X, (n, sequenceLength, 1)) / float(vocabSize)
Y = keras.utils.np_utils.to_categorical(Y)

# =============================================================================

model = keras.models.Sequential([
  keras.layers.GRU(16, input_shape=(X.shape[1], X.shape[2])),
  # keras.layers.Dropout(0.1),
  keras.layers.Dense(vocabSize),
  keras.layers.Activation("softmax"),
])

if os.access(weightsPath, os.F_OK):
  model.load_weights(weightsPath)

model.compile(loss="categorical_crossentropy", optimizer=keras.optimizers.RMSprop(lr=1e-2), metrics=["accuracy"])
