#!/usr/bin/python3

"""
First, I need to make sure that I can write to a music file. I tried doing this manually, in pure Python, and it is slow and clearly not going to be successful, The script is "MIDI.py".


Initial notes:
  The music21 library, developed by MIT, is going to be extrodinairly useful for these projects as it appears to be a pretty powerful manager capable of representing virtually any music. However, first, I'm going to need to learn how to use this.


"""




import math, random, copy, music21


def genMotif():
  def startOnRoot():
    timing = random.choice([
      [1, 2, 0.5, 0.5, 0.5, 0.5, 2, 1],
      [1, 0.5, 0.5, 1, 2, 1, 0.5, 0.5, 1],
      [2, 0.5, 0.25, 0.25, 0.5, 3, 0.5, 1]
    ])

    notes = [music21.note.Note(pitches[0])]
    notes[0].quarterLength = timing[0]

    offset = 0
    cumTime = timing[0]
    for duration in timing[1:]:
      r = random.choices([-1, 0, 1], [0.4, 0.02, 0.4])[0]
      offset += r
      # print(offset)
      note = music21.note.Note(pitches[offset])

      note.offset = cumTime
      note.quarterLength = duration

      notes.append(note)

      cumTime += duration

    # note = music21.note.Note(pitches[0])
    # note.offset = cumTime
    # note.quarterLength = timing[-1]
    # notes.append(note)

    return notes

  # def startOnFifth():
  #   return [pitches[4]]


  return random.choice([
    startOnRoot,
    # startOnFifth
  ])()


def genSection(seed=0, slow=False):
  random.seed(seed)

  motifA = motifB = random.choice(motifs)
  while motifB == motifA: motifB = random.choice(motifs)

  notes = []
  notes.extend(map(copy.deepcopy, motifA))
  notes.extend(map(copy.deepcopy, motifB))

  # c = music21.dynamics.Crescendo(notes)
  # notes.insert(0, c)
  # notes.insert(0, music21.dynamics.Dynamic("ppp"))
  # notes.insert(10, music21.dynamics.Dynamic("fff"))
  notes.insert(0, music21.dynamics.Dynamic("mf" if slow else "ff"))

  offset = 0
  for note in notes:
    note.offset = offset

    if slow: note.quarterLength *= 2
    offset += note.quarterLength

  return notes

def genSong():
  song = []

  sections = [
    genSection(seed="A"),
    genSection(seed="B", slow=True),
    genSection(seed="C"),
    genSection(seed="C", slow=True),
    genSection(seed="A")
  ]

  offset = 0
  for notes in sections:
    for note in notes:
      note.offset = offset
      song.append(note)

      offset += note.quarterLength

    # offset = notes[-1].offset + notes[-1].quarterLength

  note = music21.note.Note(progression[0])
  note.quarterLength = 2
  note.offset = offset
  song.append(note)

  return music21.stream.Part(song)

def genProgression():
  return [pitches[0], pitches[3], pitches[4], pitches[0]]

def genBasePart():
  notes = [music21.instrument.ElectricBass()]

  for i in range(math.floor(song.duration.quarterLength / 8)):
    note = music21.note.Note(progression[i % len(progression)]).transpose(-24)
    note.quarterLength = 8
    note.offset = i * 8
    notes.append(note)

  note = music21.note.Note(progression[0]).transpose(-24)
  note.quarterLength = 4
  note.offset = (i + 1) * 8
  notes.append(note)

  return music21.stream.Part(notes)

# def genDrumPart():
#   notes = [music21.instrument.Woodblock()]

#   for i in range(math.floor(song.duration.quarterLength/2)):
#     note = music21.note.Note()
#     note.offset = i*2
#     notes.append(note)

#   # note = music21.note.Note(progression[0]).transpose(-24)
#   # note.quarterLength = 4
#   # note.offset = i * 8
#   # notes.append(note)

#   return music21.stream.Part(notes)



scale = music21.scale.DorianScale("E")
pitches = scale.getPitches()
progression = genProgression() # List of notes

# print(progression)
# print(scale.getPitches())
# print(genMotif())

motifs = [genMotif() for i in range(4)]

song = genSong()
stream = music21.stream.Stream([song, genBasePart()])

# stream.insert(0, music21.instrument.Violin())
stream.write("midi", fp="output.mid")