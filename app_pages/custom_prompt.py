import streamlit as st
import base64

from chatgpt_request import request  # Your existing request function

# Import libraries for text extraction
try:
    import PyPDF2
except ImportError:
    st.error("PyPDF2 is not installed. Please install it using 'pip install PyPDF2'.")
    st.stop()

try:
    import docx
except ImportError:
    st.error("python-docx is not installed. Please install it using 'pip install python-docx'.")
    st.stop()

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file):
    try:
        return file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading TXT file: {e}")
        return ""

def custom_prompter():
    st.header("💬 Custom Prompter")
    st.write("Apply custom prompts to one or more CVs and generate tailored analyses or summaries.")

    # --- 1. UPLOAD/PASTE CVs ---
    st.subheader("Upload or Enter CVs")

    cv_texts = []
    
    uploaded_files = st.file_uploader(
        "Upload one or more CV files (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            try:
                if file.type == "application/pdf":
                    text = extract_text_from_pdf(file)
                elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text = extract_text_from_docx(file)
                elif file.type == "text/plain":
                    text = extract_text_from_txt(file)
                else:
                    st.warning(f"Unsupported file type: {file.type}")
                    continue

                if text.strip():
                    cv_texts.append({"filename": file.name, "text": text})
                else:
                    st.warning(f"No text found in {file.name}")
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

    if not cv_texts:
        st.info("Please upload CVs or enter text to proceed.")
        st.stop()

    # --- 2. CUSTOM PROMPT ---
    st.subheader("Custom Prompt")
    custom_prompt = st.text_area(
        "Enter your custom prompt here. This prompt will guide how the AI processes the CVs.",
        height=150,
        placeholder="e.g., Summarize these CVs and rank the candidates based on their fit for the Senior Developer position."
    )

    if not custom_prompt.strip():
        st.warning("Please enter a custom prompt to proceed.")

    # --- 3. PROCESS CVS ---
    st.subheader("Process CVs")
    if st.button("Generate Responses"):
        try:
            # Combine all CV texts into the prompt
            ai_prompt = custom_prompt + "\n\nCVs:\n"
            for idx, cv in enumerate(cv_texts, start=1):
                ai_prompt += f"\nCV #{idx} ({cv['filename']}):\n{cv['text']}\n"

            # Call the AI model
            with st.spinner("Generating responses..."):
                ai_response = request(ai_prompt, temperature=0.7, max_tokens=2000)

            # Display the AI response
            st.subheader("Generated Response")
            with st.expander("Show Response"):
                st.markdown(ai_response, unsafe_allow_html=True)

            # Download button for the response
            try:
                b64 = base64.b64encode(ai_response.encode()).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="AI_Response.txt">📥 Download Response</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error creating download link: {e}")

            st.success("CVs have been processed successfully.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
