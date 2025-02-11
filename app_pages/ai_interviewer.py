import streamlit as st
from streamlit_extras.bottom_container import bottom
from chatgpt_request import request
import PyPDF2
from get_job_description import get_job_description

# --- Initialization ---
initial_system_message = (
    "You are an AI interviewer and negotiator. Conduct a realistic, professional interview with the candidate by "
    "assessing their qualifications based on their CV and the job description, while also discussing work-related terms "
    "such as salary, work hours, vacation, insurance, and other benefits. Ask one question at a time and wait for the candidate's answer. "
    "Steer the conversation naturally toward negotiating work conditions and aim to reach a mutually satisfactory agreement. "
    "Once you have gathered all necessary information and finalized the negotiation, conclude the interview by including the marker "
    "[INTERVIEW_COMPLETE] in your final message, and provide a brief feedback summary along with a list of agreed-upon terms. "
    "If the candidate attempts to deviate from work-related topics, firmly bring the conversation back on track."
    "Only talk and answer in Arabic. Do not talk in English. Only Arabic is allowed in the interview."
)
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": initial_system_message}]

    if "cv_text" not in st.session_state:
        st.session_state.cv_text = ""

    if "job_description" not in st.session_state:
        st.session_state.job_description = ""

    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False

    if "waiting_for_answer" not in st.session_state:
        st.session_state.waiting_for_answer = False

    if "chat_input" not in st.session_state:
        st.session_state.chat_input = ""
        
    if "start" not in st.session_state:
        st.session_state.start = False
        
        

# --- Utility Functions ---
def extract_text_from_file(file):
    """Extract text from an uploaded PDF or TXT file."""
    try:
        if file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            text = " ".join(
                [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
            )
            return text.strip()
        else:
            return file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return ""

# --- UI Components ---

def display_assistant_message(content):
    st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 10px;">
                <div style="margin-right: 10px; font-size: 24px;">🤖</div>
                <div style="background-color: #BDBDBD; color: black; padding: 10px; border-radius: 10px; max-width: 70%;">
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_user_message(content):

    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 10px;">
            <div style="background-color: #34A853; color: black; padding: 10px; border-radius: 10px; max-width: 70%;">
                {content}
            </div>
            <div style="margin-left: 10px; font-size: 24px;">👤</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_message(role, content):
    """Render chat messages with improved styling."""
    #st.write(st.session_state.messages)

    if role == "user":
        display_user_message(content)

    else:
        display_assistant_message(content)
        
def generate_interview_prompt():
    """Generate the system prompt for the AI interviewer."""
    return (
        "You are an AI interviewer and negotiator. Conduct a structured, professional interview based on the candidate's CV and job description, "
        "and also discuss work-related terms. \n\n"
        "### Candidate Information:\n"
        f"*CV:* {st.session_state.cv_text}\n\n"
        f"*Job Description:* {st.session_state.job_description}\n\n"
        "### Interview Guidelines:\n"
        "1. Ask one question at a time and wait for the candidate's answer before proceeding.\n"
        "2. Focus the conversation on both the candidate's qualifications and work-related terms such as salary, work hours, vacation, insurance, and other benefits.\n"
        "3. If the candidate raises negotiation points, engage in a constructive negotiation to reach mutually satisfactory terms.\n"
        "4. Once sufficient information is gathered and an agreement on work terms is reached, conclude the interview by including [INTERVIEW_COMPLETE] in your final message, "
        "along with a summary of the agreed terms and feedback.\n\n"
        "### Begin the Interview:\n"
        "Ask the first relevant interview question based on the provided information."
        "Only talk and answer in Arabic. Do not talk in English. Only Arabic is allowed in the interview."
    )

def request_interview_question(prompt):
    """Request the first interview question from the AI API."""
    with st.spinner("Generating first interview question..."):
        response = request([{"role": "system", "content": prompt}])
    return response if response and not response.startswith("Error:") else "Error generating interview question."

def update_interview_state(response):
    """Update session state after generating the first question."""
    st.session_state.messages.append({"role": "assistant", "content": response})
    if response != "Error generating interview question.":
        st.session_state.interview_started = True
        st.session_state.waiting_for_answer = True

def start_interview():
    """Initiate the interview by generating the first question."""
    prompt = generate_interview_prompt()
    response = request_interview_question(prompt)
    update_interview_state(response)

def process_user_message():
    user_message = st.session_state.chat_input
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.chat_input = ""  # Clear the input
    st.session_state.waiting_for_answer = False
    
def conclude_interview(final_response):
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    st.session_state.interview_started = False
    st.session_state.waiting_for_answer = False
    
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

def upload_cv_file():
    st.subheader("Upload CV")
    cv_file = st.file_uploader("Upload your CV (PDF or TXT)", type=["pdf", "txt"], key="cv_file")
    if cv_file:
        st.session_state.cv_text = extract_text_from_file(cv_file)
        if st.session_state.cv_text:
            st.success("CV uploaded successfully!")

def load_job_description():
    st.session_state.job_description = get_job_description()

def prepare_interview():
    if not st.session_state.job_description:
        load_job_description()
    if not st.session_state.cv_text:
        upload_cv_file()

def start_interview_button():
    if st.button("Start Interview"):
        if st.session_state.cv_text and st.session_state.job_description:
            if not st.session_state.interview_started:
                start_interview()
            else:
                st.info("Interview already in progress.")
        elif (not st.session_state.cv_text) and st.session_state.job_description:
            st.error("Please upload your CV")
        elif (not st.session_state.job_description) and st.session_state.cv_text:
            st.error("Please load a job description")
        else:
            st.error("Please upload both your CV and load a job description")
            
def display_chat_history():
    for message in st.session_state.messages:
        if message["role"] != "system":
            display_message(message["role"], message["content"])

def display_interview():
    st.subheader("Interview")
    with st.container():
        display_chat_history()
        
def chat_input_area():
    with bottom():

        if st.session_state.interview_started and st.session_state.waiting_for_answer:
            st.text_input("", key="chat_input", placeholder="Type your answer here...")
            st.button("Send", on_click=submit_chat)
def session_management_buttons():
    with bottom():
        if st.button("Reset Session"):
            st.session_state.clear()
        
        if "interview_started" in st.session_state and st.session_state.interview_started:    
            if st.button("Stop Interview"):
                st.session_state.interview_started = False
                st.session_state.waiting_for_answer = False
                st.session_state.messages = [{"role": "system", "content": initial_system_message}]
            
def ai_interviewer():
    # --- Main UI ---
    st.title("AI Interview Bot")

    initialize_session_state()

    prepare_interview()

    start_interview_button()

    display_interview()
    
    chat_input_area()

    session_management_buttons()

    # --- Session Management Buttons (Pinned at the Bottom) ---