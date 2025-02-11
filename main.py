import streamlit as st
from streamlit_option_menu import option_menu
from cv_evaluation import cv_evaluation
from information_extracter import information_extracter
from cv_comparer import cv_comparer
from cv_summary import cv_summary
from cv_ranker import cv_ranker
from custom_prompt import custom_prompter
from ai_quiz import ai_quiz
from ai_interviewer import ai_interviewer
from skill_ranker import skill_ranker
from voice_ai_interview import voice_powered_ai_interviewer
# -----------------------------------------------------------------------------
# Placeholder Functions for Each Feature
# -----------------------------------------------------------------------------




# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------

def main():
    # Set up the Streamlit page configuration
    st.set_page_config(
        page_title="CV Processing App",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar for Navigation
    with st.sidebar:
        st.image("image.png", width=280)  # Replace with your logo URL or remove if not needed
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
                "Voice Powered AI Interviewer"
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
                "mic"
            ],
            menu_icon="cast",
            default_index=0,
            orientation="vertical"
        )
        st.markdown("---")
        st.write("Developed by [RMG](https://www.rmg-sa.com/en/)")  # Replace with your details

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
    elif selected == "Voice Powered AI Interviewer":
        voice_powered_ai_interviewer()


# -----------------------------------------------------------------------------
# Run the App
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
