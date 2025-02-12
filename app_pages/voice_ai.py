import sounddevice as sd
import wave
from pathlib import Path
from app_pages import st, bottom, request, get_job_description, OpenAI

if "key" not in st.session_state:
    st.session_state.key = None
else:
    client = OpenAI(api_key=st.session_state.key)


def record_audio(fs=16000):
    st.write("Recording... Speak now. Recording will stop after you pause.")
    silent_chunks = -2
    chunk_duration = 2  # seconds per chunk
    silence_duration = 5  # seconds of silence to stop recording
    num_silent_chunks = int(silence_duration / chunk_duration)
    recorded_audio = []
    
    # Placeholder to update the waveform in real time
    waveform_placeholder = st.empty()

    stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16')
    stream.start()
    try:
        while True:
            # Read a chunk of audio data
            chunk, _ = stream.read(int(fs * chunk_duration))
            chunk = chunk.flatten()
            recorded_audio.append(chunk)
            
            # Downsample for display if necessary (here we target ~500 points)
            display_length = 500
            if len(chunk) > display_length:
                factor = len(chunk) // display_length
                chunk_display = chunk[::factor]
            else:
                chunk_display = chunk

            # Update the waveform display using Streamlit's line_chart
            waveform_placeholder.line_chart(chunk_display)

            # Calculate RMS to check for silence
            rms = np.sqrt(np.mean(chunk.astype(np.float32) ** 2))
            if rms < 2000:  # Adjust threshold as necessary
                silent_chunks += 1
            else:
                silent_chunks = 0

            if silent_chunks >= num_silent_chunks:
                break
    finally:
        stream.stop()
        stream.close()
        
    st.write("Recording complete.")
    return np.concatenate(recorded_audio)


def save_audio(audio, filename="audio.wav", fs=16000):
    """Save a numpy array of audio data as a WAV file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for int16 audio
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())

def transcribe_audio(filename="audio.wav"):
    """Transcribe audio using the Whisper API."""
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text


def speak_textAI(text,voice="alloy"):
    """Generate speech from text using OpenAI's TTS model."""
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",  # Placeholder model name; replace with an actual model if available
        voice=voice,    # Choose the voice
        input=text
    )
    response.stream_to_file(str(speech_file_path))
    return str(speech_file_path)

