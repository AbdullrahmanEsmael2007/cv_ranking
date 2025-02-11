from voice_ai import *
from ai_interviewer import *
from chatgpt_request import request
import streamlit as st



def display_chat_history():
    for message in st.session_state.messages:
        if message["role"] != "system":
            display_message(message["role"], message["content"])

def display_interview():
    st.subheader("Interview")
    with st.container():
        display_chat_history()
        
def chat_input_area():
    st.subheader("Chat Input")
    st.write("Press record to talk to the interviewer.")
    if st.session_state.interview_started and st.session_state.waiting_for_answer and st.button("Record"):
        #st.text_input("", key="chat_input", placeholder="Type your answer here...")
        
        with st.spinner("Recording..."):
            audio = record_audio()
            temp_audio_file = os.path.join(tempfile.gettempdir(), "audio.wav")
            save_audio(audio, filename=temp_audio_file)
            st.audio(temp_audio_file)
            st.write("Audio saved successfully.")

        with st.spinner("Transcribing..."):
            text = transcribe_audio(temp_audio_file)
            st.write(f"Transcription: {text}")
            st.session_state.chat_input = text
            st.write( {st.session_state.chat_input})
            
        st.button("Send", on_click=submit_chat)
            
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

def convert_response_to_speech():
    voice_model = "onyx"
    
    last_msg = None
    
    for item in reversed(st.session_state.messages):
        if item["role"] == "assistant":
            last_msg = item["content"]
            break  # Stop at the first found assistant message

    # If an assistant message was found, generate audio
    if last_msg:
        audio = speak_textAI(last_msg, voice_model)
        st.audio(audio)

def voice_powered_ai_interviewer():
    
    initialize_session_state()
    
    c1,c2 = st.columns(2)
    
    with c2:
        st.title("Voice-powered AI Interviewer")
        st.write("Welcome to the Voice-powered AI Interviewer. You can ask me anything and I will respond to you.")
        prepare_interview()
        start_interview_button()
        convert_response_to_speech()
        st.write(st.session_state)
    
    with c1:
        chat_input_area()
    
    #st.write(st.session_state.messages)
    
    session_management_buttons()
    