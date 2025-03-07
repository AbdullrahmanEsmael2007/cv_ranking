from app_pages import st,bottom,request,extract_text_from_docx,extract_text_from_pdf,extract_text_from_txt,base64,re


def information_extracter():
    st.title("Data Extracter")
    st.write("Submit a CV and select what sections you would like to extract.")



    # If toggled is True, user can paste text. Otherwise, they can upload a file.

    cv_file = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])
    cv_text = ""
    if cv_file is not None:
        if cv_file.type == "application/pdf":
            cv_text = extract_text_from_pdf(cv_file)
        elif cv_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            cv_text = extract_text_from_docx(cv_file)
        elif cv_file.type == "text/plain":
            cv_text = extract_text_from_txt(cv_file)

    # Allow multiple selections of information
    information_options = st.multiselect(
    "Which sections would you like to extract?",
    [
        "Accomplishments",
        "Knowledge",
        "Education",
        "Projects",
        "Strength",
        "Weakness",
        "Certifications",
        "Awards",
        "Skills",
        "Work Experience",
        "Leadership",
        "Volunteering",
        "Languages",
        "Hobbies & Interests",
        "Publications",
        "Soft Skills",
        "Technical Skills"
    ],
    default=["Skills"]  # just a default
)


    # Let user define how many entries for each category
    amount = st.slider("Approx. amount of each selected item:", min_value=1, max_value=12, value=3)
    global temperature
    # Optional advanced settings for ChatGPT
    with st.expander("Advanced Settings"):
        temperature = st.slider("Temperature (creativity vs. focus)", 0.0, 1.0, 0.7, 0.1)
        st.caption("A higher temperature may give more creative answers, while lower values are more focused.")

    # Additional feature: Summarize the CV
    summarize_cv = st.checkbox("Also generate a quick summary of the CV?")

    # Additional feature: Keyword highlighting
    keyword_to_highlight = st.text_input("Optional: Highlight this keyword in the extracted text", "")

    # Button to start extracting
    with bottom():
        clicked = st.button("Start extracting!")

    # If button is clicked and we have some CV text
    if clicked and cv_text and information_options:

        # Build a prompt that asks for each chosen category
        # (we ask the model to label them for clarity)
        categories_str = ", ".join(information_options)
        prompt = f"""
        You are given a CV. Extract (about {amount} items per category) the following sections:
        {categories_str}.
        Present them in a clear, concise, and well-structured list under each heading.

        CV TEXT:
        {cv_text}
        """

        if summarize_cv:
            prompt += """
            
            Then provide a short, high-level summary of the CV in about 3-5 sentences.
            Label it as "Summary:" at the end.
            """

        with st.spinner("Extracting information..."):
            # Pass temperature or other parameters if your 'request' function supports them
            answer = request(prompt, temperature=temperature)

        # Display the results
        with st.expander("Extraction Results"):
            # If the user wants to highlight a specific keyword, do it here:
            if keyword_to_highlight.strip():
                # Simple highlight by wrapping keyword in HTML
                pattern = re.compile(re.escape(keyword_to_highlight), re.IGNORECASE)
                highlighted = pattern.sub(
                    f"<mark style='background-color: yellow;'>{keyword_to_highlight}</mark>",
                    answer
                )
                st.write(highlighted, unsafe_allow_html=True)
            else:
                st.write(answer)

        # Optionally allow user to download the raw answer as a .txt file


