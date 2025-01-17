from mido import MidiFile, MidiTrack, Message
import random

def generate_counterpoint(input_midi_path, output_midi_path, key_signature):
    # Define consonant intervals
    CONSONANT_INTERVALS = [0, 3, 4, 7, 8, 9, 12, 15, 16]  # Unison, M3, m3, P5, M6, m6, Octave, compound intervals

    # Load input MIDI file
    input_midi = MidiFile(input_midi_path)
    melody_notes = []

    for track in input_midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                melody_notes.append(msg.note)

    # Determine tonic note from key signature
    key_map = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
        'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }
    tonic = key_map[key_signature[0]]  # e.g., 'C'
    major_scale = [0, 2, 4, 5, 7, 9, 11]

    # Adjust scale for minor key
    if key_signature.endswith('m'):
        major_scale[2] -= 1
        major_scale[5] -= 1
        major_scale[6] -= 1

    scale = [(tonic + step) % 12 for step in major_scale]

    # Generate counter-melody notes
    counter_melody = []
    prev_interval = None
    leaps = 0

    for i, note in enumerate(melody_notes):
        # Find consonant notes in the scale
        possible_notes = [n for n in range(note - 12, note + 12) if (n - note) % 12 in CONSONANT_INTERVALS and n % 12 in scale]

        # Filter based on parallel fifths/octaves
        if prev_interval in [7, 12]:
            possible_notes = [n for n in possible_notes if (n - note) % 12 != prev_interval]

        # Avoid tritone and augmented seconds
        # possible_notes = [n for n in possible_notes if (n - note) % 12 != 6 and abs(counter_melody[-1] - n) != 3 if counter_melody else True]

        # Handle leaps and successive leaps
        if leaps >= 3 or (len(counter_melody) > 1 and abs(counter_melody[-1] - counter_melody[-2]) > 4):
            possible_notes = [n for n in possible_notes if abs(counter_melody[-1] - n) <= 2]

        # Ensure a valid note is chosen
        if not possible_notes:
            possible_notes = [note]  # Fallback to unison if no valid note is found

        selected_note = random.choice(possible_notes)

        # Update leap count
        if len(counter_melody) > 0 and abs(selected_note - counter_melody[-1]) > 4:
            leaps += 1
        else:
            leaps = 0

        counter_melody.append(selected_note)
        prev_interval = abs(selected_note - note) % 12

    # Ensure proper cadence resolution
    if counter_melody[-1] % 12 != tonic:
        counter_melody[-1] = tonic

    # Create output MIDI file
    output_midi = MidiFile()
    melody_track = MidiTrack()
    counterpoint_track = MidiTrack()

    output_midi.tracks.append(melody_track)
    output_midi.tracks.append(counterpoint_track)

    for note in melody_notes:
        melody_track.append(Message('note_on', note=note, velocity=64, time=480))
        melody_track.append(Message('note_off', note=note, velocity=64, time=480))

    for note in counter_melody:
        counterpoint_track.append(Message('note_on', note=note, velocity=64, time=480))
        counterpoint_track.append(Message('note_off', note=note, velocity=64, time=480))

    # Save the counterpoint MIDI file
    output_midi.save(output_midi_path)

# Example usage
generate_counterpoint('input_melody.mid', 'counterpoint.mid', 'C')