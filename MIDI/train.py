#!/usr/bin/python3
import keras
from utility import *

checkpoint = keras.callbacks.ModelCheckpoint(
	weightsPath,
	monitor="loss",
	verbose=0,
	save_best_only=True,
  save_weights_only=True,
  mode="auto"
)

# reduceLR = keras.callbacks.ReduceLROnPlateau(
#   monitor="loss",
#   patience=20,
#   factor=0.5,
#   verbose=2,
# )

model.fit(notesX, [notesY, offsetDurationY], epochs=1000, batch_size=2500, callbacks=[checkpoint])
