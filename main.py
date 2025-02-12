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
        page_title="تطبيق معالجة السيرة الذاتية",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if "key" not in st.session_state:
        st.session_state.key = None
    
    if st.session_state.key is None:
        st.title("مفتاح API")
        st.write("مفتاح API مطلوب لاستخدام هذا التطبيق. يرجى إدخال مفتاح API الخاص بك أدناه:")
        st.write("ليس لديك مفتاح API؟ اضغط [هنا](https://platform.openai.com/account/api-keys) للحصول عليه.")
        key = st.text_input("أدخل مفتاح OpenAI API الخاص بك", value=st.session_state.key if "key" in st.session_state else "")
        if key is not None and st.button("حفظ المفتاح"):
            st.session_state.key = key
            st.write(f"مفتاح API الخاص بك: **{key}**")
            st.button("تأكيد")
        

    else:
    # Sidebar for Navigation
        with st.sidebar:
            st.image("assets/image.png", width=280)  # Replace with your logo URL or remove if not needed
            st.title("أدوات السيرة الذاتية")
            selected = option_menu(
                menu_title=None,  # Hide the menu title
                options=[
                    "مستخرج المعلومات",
                    "مقارنة السيرة الذاتية",
                    "تقييم السيرة الذاتية",
                    "ملخص السيرة الذاتية",
                    "ترتيب السيرة الذاتية",
                    "موجه مخصص",
                    "اختبار AI",
                    "مقابلة AI",
                    "ترتيب المهارات",
                    "مقابلة AI بالصوت"
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
            setting = st.button("الإعدادات")
            if setting:
                settings()
            st.markdown("---")
            st.write("تم التطوير بواسطة [RMG](https://www.rmg-sa.com/en/)")  # Replace with your details

        # Display the selected page's content
        if selected == "مستخرج المعلومات":
            information_extracter()
        elif selected == "مقارنة السيرة الذاتية":
            cv_comparer()
        elif selected == "تقييم السيرة الذاتية":
            cv_evaluation()
        elif selected == "ملخص السيرة الذاتية":
            cv_summary()
        elif selected == "ترتيب السيرة الذاتية":
            cv_ranker()
        elif selected == "موجه مخصص":
            custom_prompter()
        elif selected == "اختبار AI":
            ai_quiz()
        elif selected == "مقابلة AI":
            ai_interviewer()
        elif selected == "ترتيب المهارات":
            skill_ranker()
        elif selected == "مقابلة AI بالصوت":
            voice_powered_ai_interviewer()


# -----------------------------------------------------------------------------
# Run the App
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

