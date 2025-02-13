import logging
from openai import OpenAI
import streamlit as st
from streamlit_option_menu import option_menu
from app_pages.cv_evaluation import cv_evaluation
from app_pages.information_extracter import information_extracter
from app_pages.cv_comparer import cv_comparer
from app_pages.cv_summary import cv_summary
from app_pages.cv_ranker import cv_ranker
from app_pages.custom_prompt import custom_prompter
from app_pages.ai_quiz import ai_quiz
from app_pages.ai_interviewer import ai_interviewer
from app_pages.skill_ranker import skill_ranker
from app_pages.voice_ai_interview import voice_powered_ai_interviewer

# Set up logging
logging.basicConfig(level=logging.INFO)

def is_api_key_valid(key):
    client = OpenAI(api_key=key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages="This is a test.",
            max_tokens=5
        )
        return True
    except Exception as e:
        logging.error(f"API key validation error: {e}")
        return False

def get_api_key():
    if "key" not in st.session_state:
        st.session_state.key = None

    if st.session_state.key is None:
        st.title("API key")
        st.write("API key is required to use this app. Please enter your API key below:")
        st.write("Don't have an API key? Click [here](https://platform.openai.com/account/api-keys) to get one.")
        key = st.text_input("Enter your OpenAI API key", value=st.session_state.key if "key" in st.session_state else "")
        if key and st.button("Save Key"):
            if not is_api_key_valid(key):
                st.error("Invalid API key. Please try again.")
            else:
                st.session_state.key = key
                st.success("API key saved successfully.")
    return st.session_state.key is not None

def render_sidebar():
    with st.sidebar:
        st.image("assets/image.png", width=280)  # Replace with your logo URL or remove if not needed
        st.title("CV Toolkit")
        selected = option_menu(
            menu_title=None,  # Hide the menu title
            options=[
                "Information Extracter",
                "CV Comparer",
                "CV Evaluation",
                "CV Summary",
                "CV Ranker",
                "Custom Prompter",
                "AI Quiz",
                "AI Interview",
                "Skill Ranker",
                "Voice AI Interview"
            ],
            icons=[
                "clipboard-data",
                "arrows-collapse",
                "clipboard-check",
                "file-earmark-text",
                "list-task",
                "chat-left-text",
                "chat-left-dots",
                "chat-left",
                "bar-chart",
                "mic"
            ],
            menu_icon="cast",
            default_index=0,
            orientation="vertical"
        )
        st.markdown("---")
        if st.button("Settings"):
            st.subheader("Settings")
            st.write(f"API Key: **{'*' * len(st.session_state.key)}**")
        st.markdown("---")
        st.write("Developed by [RMG](https://www.rmg-sa.com/en/)")  # Replace with your details
    return selected

def main():
    st.set_page_config(
        page_title="CV Processing App",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if get_api_key():
        selected = render_sidebar()
        # Display the selected page's content
        if selected == "Information Extracter":
            information_extracter()
        elif selected == "CV Comparer":
            cv_comparer()
        elif selected == "CV Evaluation":
            cv_evaluation()
        elif selected == "CV Summary":
            cv_summary()
        elif selected == "CV Ranker":
            cv_ranker()
        elif selected == "Custom Prompter":
            custom_prompter()
        elif selected == "AI Quiz":
            ai_quiz()
        elif selected == "AI Interview":
            ai_interviewer()
        elif selected == "Skill Ranker":
            skill_ranker()
        elif selected == "Voice AI Interview":
            voice_powered_ai_interviewer()

if __name__ == "__main__":
    main()