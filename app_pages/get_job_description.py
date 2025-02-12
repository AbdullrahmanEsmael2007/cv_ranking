from app_pages import st

from app_pages.convert_into_text import convert

def get_job_description():
    """
    Prompts the user to provide a job description either by:
    1) Uploading a file (pdf, docx, or txt), or
    2) Entering text directly.

    Returns the extracted or typed job description text.
    """
    st.subheader("Upload Job Description")

    # Toggle between file upload or text input
    # Option to upload a file
    job_des = st.file_uploader(
        "Upload Job Description (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"]
    )

    job_description_text = convert(job_des)

    
    return job_description_text