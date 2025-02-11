import streamlit as st
from extract_docx_pdf_txt import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from chatgpt_request import request  # Your function that calls the LLM (e.g. ChatGPT)
import base64
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

def cv_ranker():
    st.title("CV Ranker")

    st.write("""
    **Instructions**:
    1. Upload one or more CVs below.
    2. Provide a Job Description.
    3. Choose a ranking category (e.g., "Overall Strength," "Soft Skills," "Technical Skills," etc.).
    4. Click **"Rank CVs"** to generate a leaderboard of candidates by name.
    5. The AI will also propose a **score cutoff** (0–100). We'll draw a line on the leaderboard to show who's above/below that threshold.
    6. Expand any candidate row to view their entire CV text or optionally download it.
    """)

    col1, col2 = st.columns(2)
    with col1:
        cv_entries = get_cv_entries()
    
    with col2:
        job_description = get_job_description()

    toggle_css = """
    <style>
    label[data-baseweb="checkbox"] > div:first-child {
        background: #A9A9A9 !important;
    }
    label[data-baseweb="checkbox"] input:checked + div:first-child > div {
        transform: translateX(24px);
    }
    </style>
    """
    st.markdown(toggle_css, unsafe_allow_html=True)

    # --- 3. SELECT RANKING CATEGORY ---
    st.subheader("Ranking Category")
    ranking_category = st.selectbox(
        "Choose the criterion for ranking the CVs (in addition to overall fit for the job).",
        [
            "Fit for the Job",
            "Overall Strength",
            "Experience Level",
            "Leadership Potential",
            "Project Expertise",
            "Technical Skills",
            "Soft Skills"
        ]
    )

    # --- 4. ADVANCED LLM SETTINGS (optional) ---
    with st.expander("Advanced LLM Settings"):
        temperature = st.slider("Temperature (creativity vs. focus)", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input(
            "Max tokens (approximate response length)",
            min_value=200,
            max_value=4000,
            value=1200,
            step=100
        )
        st.caption("Lower temperature = more deterministic/focused output; higher = more creative.")

    # --- 5. RANK BUTTON ---
    if st.button("Rank CVs"):
        if not cv_entries:
            st.warning("Please upload at least one CV.")
            return
        if not job_description.strip():
            st.warning("Please provide a job description so the AI knows what the job requires.")
            return

        # 5a. Extract each candidate's name
        st.info("Extracting names from each CV...")
        for entry in cv_entries:
            entry["name"] = extract_name(entry["raw_text"])

        # 5b. Build the ranking prompt, including the job description & category
        ranking_prompt = build_ranking_prompt(cv_entries, job_description, ranking_category)

        # 5c. Call the LLM to rank
        st.info("Ranking CVs and obtaining cutoff score from the LLM...")
        llm_response = request(
            ranking_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # 5d. Parse the ranking & cutoff
        parsed_data = parse_ranking_response(llm_response, cv_entries)
        ranking_data = parsed_data["ranking"]
        cutoff_score = parsed_data["cutoff_score"]

        # 5e. Display the Leaderboard
        display_leaderboard(ranking_data, cv_entries, cutoff_score,job_description)


# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------

def get_cv_entries():
    st.subheader("Upload CVs")

    cv_files = st.file_uploader(
            "Upload one or more CV files (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )

    # Store each CV in a structure: [{'filename': ..., 'raw_text': ...}, ...]
    cv_entries = []
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

                cv_entries.append({
                    "filename": file.name,
                    "raw_text": raw_text
                })

    return cv_entries

def extract_name(raw_text):
    """
    Extract the person's name using a small LLM prompt, or fall back to 'Unknown'
    if not found. This is optional - you could do name extraction with 
    regex or a more robust model if you like.
    """
    name_prompt = f"""
    You have the following CV text:
    {raw_text}

    Please extract the person's full name if clearly stated. 
    If you cannot confidently find a single name, answer 'Unknown' with no extra text.
    Return ONLY the name or 'Unknown'.
    """
    try:
        resp = request(name_prompt, temperature=0.0, max_tokens=50)
        candidate_name = resp.strip().replace('"', '').replace("'", "")
        # Basic sanity check: if the result is too long or has more than 5 words, assume it's invalid
        if len(candidate_name.split()) > 5:
            return "Unknown"
        return candidate_name
    except:
        return "Unknown"


def build_ranking_prompt(cv_entries, job_description, ranking_category):
    """
    Instruct the LLM to:
    1) Rank these CVs from best to worst based on:
       - The provided job description
       - The chosen 'ranking_category'
    2) Provide a numeric score (0–100)
    3) Provide a rationale
    4) Provide a single 'cutoff_score' to separate "hire-worthy" from the rest

    We ask for a JSON object:
    {
      "ranking": [
        {
          "name": "...",
          "rank": 1,
          "score": 92,
          "rationale": "..."
        },
        ...
      ],
      "cutoff_score": 75
    }
    """
    instructions = f"""
    You are given a job description and multiple CVs. 
    **Job Description**:
    {job_description}

    The user also wants you to focus on the category: {ranking_category}
    when evaluating how well each CV matches this job.

    **Your tasks**:
    1. Rank these CVs from best to worst with regard to the job description 
       and the category '{ranking_category}' (on a scale from 0 to 100).
    2. Provide a numeric score for each candidate on a 0–100 scale (0 = worst fit, 100 = best fit).
    3. Provide a brief rationale for each candidate's rank and score.
    4. Determine a "cutoff_score" on the same 0–100 scale for who is recommended to be hired.

    Return a single JSON object with exactly two keys:
      "ranking": (an array of objects, sorted by best rank first)
      "cutoff_score": (a numeric value)

    In "ranking", each object must have:
      "name": (the name exactly as given, or "Unknown")
      "rank": (1 = best, 2 = second, etc.)
      "score": (a number between 0 and 100)
      "rationale": (brief explanation)

    Example:
    {{
      "ranking": [
        {{
          "name": "John Doe",
          "rank": 1,
          "score": 95,
          "rationale": "Excellent experience relevant to the job..."
        }},
        ...
      ],
      "cutoff_score": 80
    }}

    NO extra commentary or text, just valid JSON.
    """

    # Build the CV listing
    cv_listing = ""
    for i, entry in enumerate(cv_entries, start=1):
        name = entry["name"]
        cv_text = entry["raw_text"]
        cv_listing += f"\nCV #{i} (Name: {name}):\n{cv_text}\n"

    prompt = instructions + "\n" + cv_listing
    return prompt


def parse_ranking_response(llm_response, cv_entries):
    """
    Expects a JSON object:
    {
      "ranking": [...],
      "cutoff_score": ...
    }

    If parsing fails, we fallback to a minimal ranking with no meaningful cutoff.
    """
    # Locate the JSON portion
    start_idx = llm_response.find("{")
    end_idx = llm_response.rfind("}")
    if start_idx == -1 or end_idx == -1:
        st.error("Could not find a JSON object in the LLM response. Displaying raw response.")
        st.write(llm_response)
        return fallback_data(cv_entries)

    json_str = llm_response[start_idx:end_idx+1]
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        st.error("Could not parse JSON from the LLM response. Displaying raw response.")
        st.write(llm_response)
        return fallback_data(cv_entries)

    # Minimal validation
    if not isinstance(data, dict):
        st.error("The LLM returned JSON that isn't a dictionary. Displaying raw response.")
        st.write(llm_response)
        return fallback_data(cv_entries)

    if "ranking" not in data or "cutoff_score" not in data:
        st.error("Missing 'ranking' or 'cutoff_score' in the JSON. Displaying raw response.")
        st.write(llm_response)
        return fallback_data(cv_entries)

    # Check that ranking is a list
    if not isinstance(data["ranking"], list):
        st.error("'ranking' is not a list. Displaying raw response.")
        st.write(llm_response)
        return fallback_data(cv_entries)

    return data


def fallback_data(cv_entries):
    """
    If the LLM didn't provide valid data, just create a simple fallback
    with no meaningful cutoff. We'll put the cutoff at 0.
    """
    fallback_ranking = []
    for i, entry in enumerate(cv_entries, start=1):
        fallback_ranking.append({
            "name": entry["name"],
            "rank": i,
            "score": 0,
            "rationale": "No valid LLM response. Fallback ranking."
        })

    return {
        "ranking": fallback_ranking,
        "cutoff_score": 0
    }

def get_job_description():
    """
    Prompts the user to provide a job description either by:
    1) Uploading a file (pdf, docx, or txt), or
    2) Entering text directly.

    Returns the extracted or typed job description text.
    """
    st.subheader("Job Description")

    # Toggle between file upload or text input
    toggle_desc = False

    job_description_text = ""

    if toggle_desc:
        # Option to paste/enter text
        job_description_text = st.text_area(
            "Enter/Paste the Job Description here",
            height=77
        )
    else:
        # Option to upload a file
        job_desc_file = st.file_uploader(
            "Upload Job Description (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"]
        )
        if job_desc_file is not None:
            if job_desc_file.type == "application/pdf":
                job_description_text = extract_text_from_pdf(job_desc_file)
            elif job_desc_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                job_description_text = extract_text_from_docx(job_desc_file)
            elif job_desc_file.type == "text/plain":
                job_description_text = extract_text_from_txt(job_desc_file)

    return job_description_text

def display_leaderboard(ranking_data, cv_entries, cutoff_score, job_desc_text):
    """
    Displays the ranking in a leaderboard format with both a bar chart and a radar chart showing scores.
    """
    st.subheader("Leaderboard & AI-Recommended Cutoff (0–100 scale)")

    # Sort by rank, just in case the JSON wasn't strictly sorted
    ranking_data = sorted(ranking_data, key=lambda x: x.get("rank", 999999))

    # Extract names and scores for plotting
    names = [item.get("name", "Unknown") for item in ranking_data]
    scores = [float(item.get("score", 0)) for item in ranking_data]

    # Setup layout
    col1, col2 = st.columns(2)

    # Bar chart setup
    with col1:
        fig_bar, ax_bar = plt.subplots(figsize=(5, 4))
        ax_bar.barh(names, scores, color=["green" if s >= cutoff_score else "red" for s in scores])
        ax_bar.axvline(x=cutoff_score, color='blue', linestyle='dashed', label=f'Cutoff: {cutoff_score}')
        ax_bar.set_xlabel("Score")
        ax_bar.set_ylabel("Candidates")
        ax_bar.set_title("Candidate Scores Bar Chart")
        ax_bar.legend()
        st.pyplot(fig_bar)

    # Radar chart setup
    

    # Display table with ranking, names, and scores
    df = pd.DataFrame(ranking_data)[["rank", "name", "score", "rationale"]]
    df.columns = ["Rank", "Name", "Score", "Reasoning"]
    st.write("### Leaderboard Table")
    st.dataframe(df)

    # Show the chosen cutoff for clarity
    st.write(f"\n**AI-Recommended Cutoff Score**: {cutoff_score}")



def find_cv_text_by_name(name, cv_entries):
    """
    Attempt to find the correct CV text for the given 'name'. 
    If names are "Unknown" or duplicates, we might pick the first match.
    """
    if name == "Unknown":
        for entry in cv_entries:
            if entry["name"] == "Unknown":
                return entry["raw_text"]
        return None
    # Otherwise, match exact name
    for entry in cv_entries:
        if entry["name"] == name:
            return entry["raw_text"]
    return None
