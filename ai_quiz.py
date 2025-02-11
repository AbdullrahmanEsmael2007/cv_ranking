import streamlit as st
from chatgpt_request import request  # Assuming this is your custom module
from get_job_description import get_job_description


def ai_quiz():
    st.title("AI-Powered Quiz")

    # Initialize session state for questions if it doesn't exist
    if "questions" not in st.session_state:
        st.session_state.questions = []

    # Input fields for name, job description, and CV
    name = st.text_input("Enter your name:")
    job_description = get_job_description()


    # Toggleable CV input (file upload or text input)
    cv_option = st.radio("Choose CV input method:", ("File Upload", "Text Input"))

    if cv_option == "File Upload":
        cv_file = st.file_uploader("Upload your CV (PDF or TXT):", type=["pdf", "txt"])
        if cv_file:
            cv_text = cv_file.read().decode("utf-8") if cv_file.type == "text/plain" else "PDF content extraction not implemented."
        else:
            cv_text = ""
    else:
        cv_text = st.text_area("Paste your CV here:")

    amount = st.slider("Number of Questions", 3, 10, 5)
    level = st.select_slider(
    "Level",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    # Generate interview questions
    if st.button("Generate Interview Questions"):
        if not name or not job_description or not cv_text:
            st.error("Please fill in all fields.")
        else:
            # Create a prompt for generating questions
            prompt = f"""
            Name: {name}
            Job Description: {job_description}
            CV: {cv_text}

            Generate {amount} interview questions based on the above information and based on the CV.Make them be related to the job description.The difficulty level is {level}. Take the level literally. Only give the questions without any titles
            """
            response = request(prompt)  # Assuming this returns a string with questions separated by newlines
            questions = response.split("\n")  # Split the response into individual questions
            questions = [q.strip() for q in questions if q.strip()]  # Clean up the questions

            if len(questions) < 1:
                st.error("Failed to generate enough questions. Please try again.")
            else:
                st.session_state.questions = questions[:5]  # Store questions in session state
                st.success("Questions generated successfully!")

    # Display questions and answer fields
    if st.session_state.questions:
        st.subheader("Interview Questions")
        answers = []
        for i, question in enumerate(st.session_state.questions):
            st.write(f"**Question {i+1}:** {question}")
            answer = st.text_area(f"Your answer to Question {i+1}:", key=f"answer_{i}")
            answers.append(answer)

        strictness = st.select_slider("Strictness",["Very Strict", "Strict", "Moderately Strict", "Moderate", "Relaxed", "Very Relaxed"])

        # Evaluate answers
        if st.button("Submit Answers"):
            if not all(answers):
                st.error("Please answer all questions.")
            else:
                # Create a prompt for evaluating answers
                evaluation_prompt = f"""
                Job Description: {job_description}
                CV: {cv_text}
                Strictness: {strictness}

                Questions and Answers:
                """
                for i, (question, answer) in enumerate(zip(st.session_state.questions, answers)):
                    evaluation_prompt += f"\nQuestion {i+1}: {question}\nAnswer: {answer}\n"

                evaluation_prompt += "\nEvaluate the answers and provide a score out of 10."
                evaluation_result = request(evaluation_prompt)
                st.subheader("Evaluation Result")
                st.write(evaluation_result)
