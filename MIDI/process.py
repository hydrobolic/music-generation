#!/usr/bin/python3

import os, music21, glob, pickle

# times = [0, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 1, 3/2, 2, 3, 4, 8, 1/12, 1/6, 1/3, 2/3] # Non exhaustive list
# times = [0, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 1, 3/2, 2, 4, 8] # Non exhaustive list
# times = [0, 1/8, 1/4, 1/2, 3/4, 1, 3/2, 2, 4, 8] # Non exhaustive list
times = [1/4, 1/2, 1, 3/2, 2, 3, 4, 6, 8, 16] # Non exhaustive list

def nearest(q, l):
  return min(l, key=lambda x: abs(q - x))

# Inefficient as we already parsed the songs twice and writing to a MIDI file which isn't necessary

outputPath = "songs/input"
notesPath = "notesCache"
encodingPath = "encoder"

# songs = [
#   "songs/midi_songs/gerudo.mid",
#   "songs/midi_songs/JENOVA.mid",
#   "songs/midi_songs/decisive.mid",
#   "songs/midi_songs/FF4.mid",
#   "songs/midi_songs/FF3_Battle_(Piano).mid",
#   "songs/midi_songs/great_war.mid",
#   "songs/midi_songs/dayafter.mid",
# #   "songs/CymaticShort.mid",
#   "songs/faure-dolly-suite-1-berceuse.mid",
#   # "songs/herbie/Herbie Hancock chameleon.mid",
# ]

# songs = [f"songs/herbie/{fp}" for fp in os.listdir("songs/herbie")]
# songs = [
#   "songs/herbie/Herbie Hancock chameleon.mid",
#   "songs/herbie/Herbie Hancock Cantalope Island.mid",
# ]

# songs = ["songs/bach/Bach_2PartInv_No8_in_F_BWV779.mid"]
# songs = [f"songs/bach/{fp}" for fp in os.listdir("songs/bach")]

# songs = ["songs/franz-schubert-standchen-serenade-piano-solo.mid"]

# songs = [
#   "songs/Relax/ChopinNocturne.mid",
#   "songs/franz-schubert-standchen-serenade-piano-solo.mid",
#   "songs/bach/Bach_2PartInv_No8_in_F_BWV779.mid",
#   "songs/faure-dolly-suite-1-berceuse.mid",
# ]

songs = ["songs/lstm/train.midi"]

# songs = [f"songs/lstm/{fp}" for fp in os.listdir("songs/lstm")]

notes = []

off = 0
for f in songs:
  print(f"Processing song '{f}'")

  midi = music21.converter.parse(f)
  n = midi.flat.notes

  threshhold = music21.note.pitch.Pitch("C2")

  shift = -off

  for i, element in enumerate(n):
    # if i > 200: continue
    # if isinstance(element, music21.chord.Chord):
    #   element = element.root()

    # element.quarterLength = 0.5

    if 0 < i < len(n) - 1:  
      if isinstance(element, music21.note.Note) and element.pitch > threshhold or isinstance(element, music21.chord.Chord):
        element.offset = n[i].offset - shift
        # if len(notes) == 0 or element.offset != notes[-1].offset:
        notes.append(element)

      else: shift += n[i].offset - n[i - 1].offset

  off += notes[-1].offset

print(f"\nWriting to {outputPath}/processed.mid")
stream = music21.stream.Stream(notes)
stream.augmentOrDiminish(0.7, inPlace=True)
stream.write("midi", fp=f"{outputPath}/processed.mid")

# music21.converter.parse(songs[0]).write("midi", fp=f"{outputPath}/processed.mid")


# =============================================================================

print("\n")

# def getImmutableNotes(notes):
#   if len(notes) == 0: return []

#   def getTuple(r, rOff):
#     if isinstance(r, music21.note.Note): return (r.pitch, nearest(r.quarterLength, times), nearest(rOff, times))
#     return (r.pitches, nearest(r.quarterLength, times), nearest(rOff, times))

#   immutableNotes = [getTuple(notes[0], 0)]

#   for i, note in enumerate(notes):
#     if i == 0: continue;
#     immutableNotes.append(getTuple(note, notes[i].offset - notes[i - 1].offset))
#   return immutableNotes

for f in glob.glob(f"{outputPath}/*.mid"):
  print("Parsing %s" % f)

  midi = music21.converter.parse(f)

  for element in midi.flat.notes:
    if isinstance(element, music21.note.Note): notes.append(element)

if len(notes) != 0:
  n = []
  o = []
  d = []

  with open(notesPath, "wb") as f:
    def getPitch(n):
      return n.pitches if isinstance(n, music21.chord.Chord) else n.pitch

    n = [getPitch(notes[0])]
    offsets = [0]
    d = [nearest(notes[0].quarterLength, times)]
    for i, note in enumerate(notes):
      if i == 0: continue
      n.append(getPitch(note))
      o.append(nearest(notes[i].offset - notes[i - 1].offset, times))
      d.append(nearest(note.quarterLength, times))

    pickle.dump([n, o, d], f)


  with open(encodingPath, "wb") as f:
    pickle.dump(list(set(n)), f)
