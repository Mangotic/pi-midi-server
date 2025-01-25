from flask import Flask, render_template, request, send_from_directory
import mido
import threading
import time
import os
from datetime import datetime

app = Flask(__name__)

recording = False
midi_dir = "/home/pi/midi_recordings"  # Folder for MIDI files

# Ensure the directory exists
if not os.path.exists(midi_dir):
    os.makedirs(midi_dir)

def find_midi_device():
    """Finds the first available MIDI input device automatically."""
    devices = mido.get_input_names()
    if devices:
        return devices[0]  # Use the first available MIDI device
    return None

def get_midi_files():
    """Returns a sorted list of recorded MIDI files."""
    files = sorted(os.listdir(midi_dir), reverse=True)  # Latest files first
    return files

def record_midi():
    """Records MIDI input and saves it to a time-stamped file."""
    global recording

    midi_port = find_midi_device()
    if not midi_port:
        print("No MIDI device found!")
        recording = False
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    midi_file_path = os.path.join(midi_dir, f"recording_{timestamp}.mid")

    with mido.open_input(midi_port) as inport:
        print(f"Recording MIDI from {midi_port}...")
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)

        start_time = time.time()

        for msg in inport:
            if not recording:
                break  # Stop recording when the flag is turned off
            msg.time = time.time() - start_time
            track.append(msg)

        mid.save(midi_file_path)
        print(f"MIDI recording saved as {midi_file_path}")

@app.route("/")
def index():
    """Main webpage with start/stop buttons and file history."""
    files = get_midi_files()
    return render_template("index.html", recording=recording, files=files)

@app.route("/start", methods=["POST"])
def start():
    """Starts MIDI recording."""
    global recording
    if not recording:
        recording = True
        threading.Thread(target=record_midi).start()
    return "Recording started!"

@app.route("/stop", methods=["POST"])
def stop():
    """Stops MIDI recording."""
    global recording
    recording = False
    return "Recording stopped!"

@app.route("/download/<filename>")
def download(filename):
    """Serves a selected MIDI file for download."""
    return send_from_directory(midi_dir, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
