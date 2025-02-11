from sympy import false
from ai_interviewer import *
from chatgpt_request import request
from pathlib import Path
import sounddevice as sd
import numpy as np
import wave
from openai import OpenAI
import os
from key import OPENAI_API_KEY
import streamlit as st
import pyaudio
import wave
import time
import tempfile

# Set up your OpenAI API key
client = OpenAI(api_key=OPENAI_API_KEY)


#record_audio(fs=16000)
#save_audio(audio, filename="audio.wav", fs=16000)
#transcribe_audio(filename="audio.wav")
#speak_textAI(text, voice="alloy")
#
#text = transcribe_audio(temp_audio_file)
#audio_file = speak_textAI(response_text,voice_model)
#st.audio(audio_file)
#
#
#initialize_session_state()
#prepare_interview() returns null
#start_interview()() returns null
#display_interview() returns null
#chat_voice_area() returns null
#session_management_buttons() returns null

st.session_state.start = False
st.session_state.frames =[]

def record_audio():
    """
    Record audio using PyAudio and display live waveform using Streamlit.

    :return: NumPy array of recorded audio data
    """
    c1, c2 = st.columns(2)
    st.session_state.stopped = False

    with c1:
        if st.session_state.start:
            st.session_state.frames = []
    with c2:
        if st.button("Stop"):
            st.session_state.stopped = True

    chunk = 1024  # Audio chunk size
    format = pyaudio.paInt16  # 16-bit audio format
    channels = 1  # Mono recording
    rate = 16000  # Sample rate

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    waveform_placeholder = st.empty()  # Placeholder for live waveform display

    try:
        while not st.session_state.stopped and st.session_state.start:
            with st.spinner("Recording..."):
                data = stream.read(chunk, exception_on_overflow=False)  # Read audio data
                st.session_state.frames.append(data)

                # Convert audio chunk to NumPy array for visualization
                chunk_array = np.frombuffer(data, dtype=np.int16)

                # Downsample for display
                display_length = 500
                if len(chunk_array) > display_length:
                    factor = len(chunk_array) // display_length
                    chunk_display = chunk_array[::factor]
                else:
                    chunk_display = chunk_array

                waveform_placeholder.line_chart(chunk_display)  # Live waveform update

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    st.write("Recording complete.")

    # Convert frames to NumPy array and return
    audio_data = np.frombuffer(b"".join(st.session_state.frames), dtype=np.int16)
    st.session_state.frames.clear()
    return audio_data

n   = record_audio()





def save_audio(audio, filename="audio.wav", fs=16000):
    """Save a numpy array of audio data as a WAV file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for int16 audio
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())
        
save_audio(n)
st.audio("audio.wav")

def transcribe_audio(filename="audio.wav"):
    """
    Transcribes audio from a given WAV file using OpenAI's Whisper model.

    :param filename: The path to the WAV file to be transcribed. 
                     Defaults to "audio.wav".
    :return: The transcribed text as a string.
    """

    audio_file= open(filename, "rb")
    st.write(f"Transcribing audio from: {filename}")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )

    return transcription.text


def speak_textAI(text,voice="alloy"):
    """Generate speech from text using OpenAI's TTS model."""
    speech_file_path = Path(__file__).parent / "speech.mp3"
    
    
    response =  client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    ) 
    response.stream_to_file(str(speech_file_path))
        
    return str(speech_file_path)

#

def display_chat_history():
    for message in st.session_state.messages:
        if message["role"] != "system":
            display_message(message["role"], message["content"])

def display_interview():
    st.subheader("Interview")
    with st.container():
        display_chat_history()
        
def chat_voice_area():
    st.subheader("Chat Input")
    st.write("Press record to talk to the interviewer.")
          # Wait for user to press SPACE
    
    if st.session_state.interview_started and st.session_state.waiting_for_answer:
        if st.button("Start"):
            st.session_state.start = True
        
    if st.session_state.start:
        #st.text_input("", key="chat_input", placeholder="Type your answer here...")
        
        audio = record_audio()
        temp_audio_file = os.path.join(tempfile.gettempdir(), "audio.wav")
        st.write(f"Recording saved as: {temp_audio_file}")
        save_audio(audio, filename=temp_audio_file)
        st.audio(temp_audio_file)
        st.write("Audio saved successfully.")

        with st.spinner("Transcribing..."):
            try:
                text = transcribe_audio(temp_audio_file)
            
                st.write(f"Transcription: {text}")
                st.session_state.chat_input = text
                st.write( {st.session_state.chat_input})
            except Exception as e:
                st.error("aassaa")
            
        st.button("Send", on_click=submit_chat)
        st.session_state.start = False
        
            
def submit_chat():
    """Process the chat submission immediately upon clicking 'Send'."""
    if st.session_state.chat_input.strip():
        process_user_message()
        
        with st.spinner("Waiting for response..."):
            response = request(st.session_state.messages)
        
        if response and not response.startswith("Error:"):
            # If the AI's response contains the marker, conclude the interview.
            if "[INTERVIEW_COMPLETE]" in response:
                final_response = response.replace("[INTERVIEW_COMPLETE]", "").strip()
                conclude_interview(final_response)
            else:
                update_interview_state(response)
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Error processing your response."})

def convert2speech():
    voice_model = "alloy"
    
    last_msg = None
    
    for item in reversed(st.session_state.messages):
        if item["role"] == "assistant":
            last_msg = item["content"]
            break  # Stop at the first found assistant message

    # If an assistant message was found, generate audio
    if last_msg:
        audio = speak_textAI(last_msg, voice_model)
        st.write(last_msg)
        st.audio(audio)

def voice_powered_ai_interviewer():
    
    initialize_session_state()
    if "frames" not in st.session_state:
        st.session_state.frames = []
    
    c1,c2 = st.columns(2)
    
    with c2:
        st.title("Voice-powered AI Interviewer")
        st.write("Welcome to the Voice-powered AI Interviewer. You can ask me anything and I will respond to you.")
        prepare_interview()
        start_interview_button()
        convert2speech()
        st.write(st.session_state)
    
    with c1:
        chat_voice_area()
    
    #st.write(st.session_state.messages)
    
    session_management_buttons()