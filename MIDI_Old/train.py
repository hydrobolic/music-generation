#!/usr/bin/python3
import keras
from utility import *

checkpoint = keras.callbacks.ModelCheckpoint(
	weightsPath,
	monitor="loss",
	verbose=0,
	save_best_only=True,
  save_weights_only=True,
	mode="min"
)

model.fit(X, Y, epochs=10000, batch_size=2500, callbacks=[checkpoint])
