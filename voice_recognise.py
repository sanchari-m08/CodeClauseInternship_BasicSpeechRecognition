import pyaudio
import wave
import speech_recognition as sr
import numpy as np

# Parameters for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = "output.wav"

def record_audio():
    # Initialize pyaudio
    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recording to a file
    with wave.open(OUTPUT_FILENAME, 'wb') as waveFile:
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))

def normalize_audio(audio_path):
    with wave.open(audio_path, 'rb') as wf:
        audio_data = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(audio_data, dtype=np.int16)
        max_val = np.max(np.abs(audio_data))
        normalized_data = (audio_data / max_val).astype(np.float32)
        
        # Save the normalized audio back to the file
        normalized_data_int16 = (normalized_data * max_val).astype(np.int16)
        with wave.open(audio_path, 'wb') as wf_normalized:
            wf_normalized.setnchannels(CHANNELS)
            wf_normalized.setsampwidth(2)  # 2 bytes (16 bits)
            wf_normalized.setframerate(RATE)
            wf_normalized.writeframes(normalized_data_int16.tobytes())

def recognize_command():
    record_audio()
    normalize_audio(OUTPUT_FILENAME)

    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Recognize speech from the recorded and normalized audio file
    with sr.AudioFile(OUTPUT_FILENAME) as source:
        audio = recognizer.record(source)

    try:
        recognized_text = recognizer.recognize_google(audio)
        print("You said: " + recognized_text)

        if "start" in recognized_text.lower():
            print("Starting the process...")
        elif "stop" in recognized_text.lower():
            print("Stopping the process...")
        elif "exit" in recognized_text.lower():
            print("Exiting the application...")
        else:
            print("Command not recognized.")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    print("Press Enter to start recording...")
    input()  # Wait for user input to begin recording
    recognize_command()
