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


def main():
    # Set up the Streamlit page configuration
    st.set_page_config(
        page_title="CV Processing App",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if "key" not in st.session_state:
        st.session_state.key = None
    
    if st.session_state.key is None:
        st.title("API key")
        st.write("API key is required to use this app. Please enter your API key below:")
        st.write("Don't have an API key? Click [here](https://platform.openai.com/account/api-keys) to get one.")
        key = st.text_input("Enter your OpenAI API key", value=st.session_state.key if "key" in st.session_state else "")
        if key is not None and st.button("Save Key"):
            st.session_state.key = key
            st.write(f"Your API-Key: **{key}**")
            st.button("Confirm")
        

    else:
    # Sidebar for Navigation
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
            setting = st.button("Settings")
            if setting:
                st.subheader("Settings")
                st.write(f"API Key: **{st.session_state.key}**")
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
        elif selected == "Voice AI Interview":
            voice_powered_ai_interviewer()


# -----------------------------------------------------------------------------
# Run the App
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
