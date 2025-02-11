import streamlit as st
from extract_docx_pdf_txt import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from chatgpt_request import request  # Your function to call ChatGPT
from streamlit_extras.bottom_container import bottom
import base64
import re

def cv_summary():
    st.title("CV Summary")
    st.write("Upload a CV or paste its text to get a concise summary with key information.")

    # --- 1. Upload/Paste CV ---
    cv_text = ""

    cv_file = st.file_uploader("Upload CV (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    if cv_file is not None:
        if cv_file.type == "application/pdf":
            cv_text = extract_text_from_pdf(cv_file)
        elif cv_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            cv_text = extract_text_from_docx(cv_file)
        elif cv_file.type == "text/plain":
            cv_text = extract_text_from_txt(cv_file)

    # --- 2. Advanced LLM Settings ---
    with st.expander("Advanced LLM Settings"):
        temperature = st.slider("Temperature (creativity vs. focus)", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input(
            "Max tokens (approximate response length)",
            min_value=200, 
            max_value=4000, 
            value=1000, 
            step=100
        )

    # --- 3. Additional Options ---
    st.subheader("Additional Options")
    highlight_word = st.text_input("Highlight a keyword (optional)")
    show_improvement = st.checkbox("Suggest how to improve this CV?")

    # --- 4. Summarize Button ---
    with bottom():
        summarize_btn = st.button("Summarize CV")

    # --- 5. Summarize Logic ---
    if summarize_btn:
        if not cv_text.strip():
            st.warning("Please upload or enter some CV text first.")
            return

        # 5a. Attempt to extract contact info (name, email, phone, etc.) in one shot
        with st.spinner("Extracting contact info..."):
            contact_info = extract_contact_info(cv_text)

        if contact_info:
            # Display the extracted info
            st.write("**Extracted Contact Info:**")
            for key, val in contact_info.items():
                if val:
                    st.write(f"- **{key.capitalize()}**: {val}")
            st.write("---")

        # Build summary prompt
        prompt = build_summary_prompt(cv_text, contact_info, show_improvement)

        with st.spinner("Generating CV Summary..."):
            summary_result = request(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

        # Display result (with optional highlight)
        final_text = summary_result
        if highlight_word.strip():
            pattern = re.compile(re.escape(highlight_word), re.IGNORECASE)
            final_text = pattern.sub(
                f"<mark style='background-color: yellow;'>{highlight_word}</mark>", 
                final_text
            )

        st.subheader("CV Summary")
        st.write(final_text, unsafe_allow_html=True)

        # Download button
        download_link = create_download_button(summary_result, "cv_summary.txt", "Download Summary")
        st.markdown(download_link, unsafe_allow_html=True)


def build_summary_prompt(cv_text, contact_info, show_improvement):
    """
    Creates a ChatGPT prompt to summarize the CV and optionally suggest improvements.
    Incorporates any extracted contact info into the prompt context if available.
    """
    name = contact_info.get("name", "Unknown")
    email = contact_info.get("email", "Unknown")
    phone = contact_info.get("phone", "Unknown")

    prompt_parts = [
        "You are given a CV. Provide a concise yet comprehensive summary, focusing on key skills, experiences, and education.",
        "Make sure to note any major accomplishments or highlights as well."
    ]

    # Add any contact info we found (just for context; the model might or might not use it directly)
    if name != "Unknown":
        prompt_parts.append(f"The person's name is {name}.")
    if email != "Unknown":
        prompt_parts.append(f"The person's email is {email}.")
    if phone != "Unknown":
        prompt_parts.append(f"The person's phone number is {phone}.")

    if show_improvement:
        prompt_parts.append("Suggest a few actionable improvements to enhance the CV.")

    prompt_parts.append(f"\nCV TEXT:\n{cv_text}\n")
    prompt = "\n".join(prompt_parts)
    return prompt


def extract_contact_info(cv_text):
    """
    Attempts to extract the person's name, email, and phone from the CV text in a single LLM call.
    If not found, return them as 'Unknown'. 
    Returns a dict: { 'name': ..., 'email': ..., 'phone': ... }
    """
    info_prompt = f"""
You are given the text of a CV. Please extract the following fields if they are clearly stated:
1) The person's full name
2) Their primary email address
3) Their phone number

If you cannot confidently determine a field, respond with 'Unknown' for that field.

Return the result in a JSON object with keys "name", "email", and "phone". Example:
{{
  "name": "...",
  "email": "...",
  "phone": "..."
}}

Only return valid JSON, no extra commentary.

CV TEXT:
{cv_text}
"""
    # Call your LLM function
    try:
        response = request(info_prompt, temperature=0.0, max_tokens=150)
        # Attempt to parse the JSON
        import json
        data = {}
        # Basic safety parse
        response = response.strip()
        # Sometimes the model might return extra text, let's extract JSON from it using a fallback approach
        # A simple approach is to find the first '{' and last '}' bracket pair and parse that substring.
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1]
            data = json.loads(json_str)
        else:
            data = {
                "name": "Unknown",
                "email": "Unknown",
                "phone": "Unknown"
            }
        # Validate keys
        for key in ["name", "email", "phone"]:
            if key not in data or not data[key].strip():
                data[key] = "Unknown"
        return data
    except:
        return {
            "name": "Unknown",
            "email": "Unknown",
            "phone": "Unknown"
        }


def create_download_button(content, filename, button_text):
    """
    Creates a download button to save `content` into `filename`.
    """
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{button_text}</a>'
