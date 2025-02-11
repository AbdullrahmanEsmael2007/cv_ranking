import streamlit as st

from PyPDF2 import PdfReader
from chatgpt_request import request
from extract_docx_pdf_txt import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt

def cv_evaluation():
    st.title("CV Evaluation")
    st.write("Enter a CV with the job description")

    job_description = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
    cv = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

    if job_description is not None:
        if job_description.type == "application/pdf":
            job_description = extract_text_from_pdf(job_description)
        elif job_description.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            job_description = extract_text_from_docx(job_description)
        elif job_description.type == "text/plain":
            job_description = extract_text_from_txt(job_description)

    if cv is not None:
        if cv.type == "application/pdf":
            cv = extract_text_from_pdf(cv)
        elif cv.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            cv = extract_text_from_docx(cv)
        elif cv.type == "text/plain":
            cv = extract_text_from_txt(cv)
        
    length = st.select_slider(
    "Choose a length",
    options=["very short", "short", "medium", "long", "very long"],
    value="medium"
    )

    clicked = st.button("Start evaluation!")


    if job_description and cv and clicked:
        prompt = f"""
            Given a job description and a CV, evaluate the CV to determine if the individual is a suitable fit for the role. 
            Provide a brief assessment, including reasons why the person is or isn’t a good match. Highlight key skills, qualifications, and experience that align with or fall short of the job requirements.
            Keep the response concise, {len} length.  Prioritize keywords and relevant phrases instead of full sentences to meet the word count.
            Job Description: {job_description}
            CV: {cv}
            Include feedback on strengths, weaknesses, and any discrepancies or gaps in experience. 
            Ensure the feedback is objective, unbiased, and based solely on the content provided in the job description and CV. Avoid subjective opinions or assumptions.
            """
        with st.spinner("Evaluating CV..."):
            evaluation = request(prompt)
            score = request(f"Give the evaluation a score from 0 to 100, where 0 is the worst match and 100 is the best match.. Evaluation: {evaluation}- Give the score only without any text.")
            shouldBeHired = request(f"Should the CV be hired?  Evaluation: {evaluation}- Give the answer only (true or false) without any text.")
        with st.expander("Evaluation",expanded=True):
            st.write(evaluation)
            
            st.slider("Score",min_value=0,max_value=100,value=int(score),disabled=True)
            print(shouldBeHired)
            if shouldBeHired.lower() == "true":
                st.success("The CV should be hired!")
            else:
                st.error("The CV should not be hired.")