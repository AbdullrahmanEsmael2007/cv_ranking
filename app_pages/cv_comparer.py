from app_pages import st, request, extract_text_from_docx, extract_text_from_pdf, extract_text_from_txt

def cv_comparer():
    st.title("CV Comparer")
    st.write("Upload any number of CVs, and I'll compare them collectively. Names are auto-extracted where possible.")

    # 1. MULTIPLE FILE UPLOAD
    st.subheader("Upload CV(s)")
    cv_files = st.file_uploader(
        "Upload one or more CV files (pdf, docx, txt)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    # 2. Parse text and attempt to extract the name from each CV
    cv_entries = []  # Will hold tuples of (person_name, cv_text)
    if cv_files:
        for file in cv_files:
            raw_text = ""
            if file.type == "application/pdf":
                raw_text = extract_text_from_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                raw_text = extract_text_from_docx(file)
            elif file.type == "text/plain":
                raw_text = extract_text_from_txt(file)

            if raw_text.strip():
                # Attempt to extract the person's name using LLM
                person_name = extract_name_from_cv(raw_text)
                cv_entries.append((person_name, raw_text))

    # 3. Let user set advanced LLM options
    with st.expander("Advanced LLM Settings"):
        temperature = st.slider("Temperature (creativity vs. focus)", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input(
            "Max tokens (approximate response length)",
            min_value=200, max_value=4000, value=1000, step=100
        )
        st.caption("Lower temperature = more deterministic/focused output; Higher = more creative.")

    # 4. Additional options
    st.subheader("Additional Options")
    highlight_word = st.text_input("Highlight a keyword in the comparison (optional)")
    suggest_improvements = st.checkbox("Suggest improvements/ways to merge these CVs?")

    # 5. Compare button at the bottom
    with bottom():
        compare_button = st.button("Compare All CVs")

    # 6. Build the prompt and call the model
    if compare_button:
        if not cv_entries:
            st.warning("Please upload at least one CV file with valid text.")
            return

        prompt = build_prompt(cv_entries, suggest_improvements)

        with st.spinner("Comparing CVs..."):
            # Make your ChatGPT request. 
            # Adjust to how your 'request' function is designed (e.g., request(prompt, temperature=..., max_tokens=...))
            comparison_result = request(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

        # 7. Display results (with optional keyword highlighting)
        st.subheader("Comparison Results")
        final_text = comparison_result
        if highlight_word.strip():
            pattern = re.compile(re.escape(highlight_word), re.IGNORECASE)
            final_text = pattern.sub(
                f"<mark style='background-color: yellow;'>{highlight_word}</mark>",
                final_text
            )
            st.write(final_text, unsafe_allow_html=True)
        else:
            st.write(final_text)

        # 8. Confetti for fun

        # 9. Download results
        download_link = create_download_button(comparison_result, "cv_comparison_results.txt", "Download Comparison")
        st.markdown(download_link, unsafe_allow_html=True)


def extract_name_from_cv(cv_text):
    """
    Attempts to extract the person's name from a CV using a separate LLM prompt.
    If not found, returns 'Unknown'.
    
    You could also implement regex or your own heuristics. But for a general approach,
    we let ChatGPT try to parse the name. This calls the same `request()` function 
    or a specialized function, depending on your setup.
    """
    name_prompt = f"""
    You are given a CV. Extract the person's full name if it's explicitly stated. 
    If you cannot confidently find the name, respond with 'Unknown'. 
    Return ONLY the name itself or 'Unknown' with no extra commentary.

    CV TEXT:
    {cv_text}
    """

    try:
        # A short, direct LLM call
        response = request(name_prompt, temperature=0.0, max_tokens=50)
        # Clean up the response (just in case)
        extracted_name = response.strip().replace('"', '').replace("'", "")
        # If the model returns anything suspicious or too long, default to 'Unknown'
        if len(extracted_name.split()) > 5:  
            extracted_name = "Unknown"
        return extracted_name
    except Exception:
        return "Unknown"


def build_prompt(cv_entries, suggest_improvements):
    """
    Constructs a single prompt to compare an arbitrary number of CVs,
    labeling each by the extracted name or 'Unknown.'
    """
    # 1) If there's only one CV, we won't do a multi-CV comparison, 
    #    but we still return a summary. 
    if len(cv_entries) == 1:
        (name, text) = cv_entries[0]
        single_cv_prompt = f"""
        A single CV is provided (Name: {name}).
        1. Summarize its strengths, weaknesses, and notable skills.
        2. Suggest an approximate 'self-similarity score' (which might trivially be 100%, 
           since there's no other CV to compare).
        """
        if suggest_improvements:
            single_cv_prompt += """
            3. Suggest how this CV might be improved to better showcase the candidate's profile.
            """
        single_cv_prompt += f"\n\nCV TEXT:\n{text}\n"
        return single_cv_prompt

    # 2) Multiple CVs
    prompt_intro = """
You are given multiple CVs. For each CV, the name extracted will be shown in parentheses. 
Please do the following:
1. Summarize the key similarities among all CVs (common skills, experiences, qualifications).
2. Summarize the key differences or unique aspects each CV brings.
3. Provide an approximate "similarity score" (0-100%) for how much overlap there is among all of them overall.
    """
    prompt_improvements = """
4. Suggest how each CV might be improved or how they could be combined into a single, stronger CV.
    """

    cv_section = ""
    for idx, (person_name, text) in enumerate(cv_entries, start=1):
        cv_section += f"\nCV #{idx} (Name: {person_name}):\n{text}\n"

    final_prompt = prompt_intro
    if suggest_improvements:
        final_prompt += prompt_improvements
    final_prompt += cv_section

    return final_prompt


def create_download_button(content, filename, button_text):
    """
    Creates a downloadable link (button) that saves 'content' into 'filename'.
    """
    b64 = base64.b64encode(content.encode()).decode()  # Convert to base64
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{button_text}</a>'
