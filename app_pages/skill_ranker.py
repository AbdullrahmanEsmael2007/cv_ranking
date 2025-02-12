import matplotlib.pyplot as plt
import json
from app_pages import st,request,pd,np,extract_text_from_docx,extract_text_from_pdf,extract_text_from_txt


def extract_name(cv_text):
    """
    Extracts the candidate's name using the LLM request function.
    """
    prompt = f"Extract the candidate's full name from the following CV text: {cv_text}. Return ONLY the name."
    name = request(prompt, temperature=0.0, max_tokens=50)
    return name.strip()

def score_section(cv_text, job_desc_text, section):
    """
    Uses the LLM to generate a score for a single section of a CV.
    """
    scoring_prompt = f"""
    Given the following job description:
    {job_desc_text}
    
    Evaluate this candidate's CV based on the section: {section}.
    
    CV:
    {cv_text}
    
    Return ONLY a valid JSON object in the format: {{"{section}": score}}, where score is a number between 0 and 100.
    No extra text, explanation, or markdown. Just the JSON.
    """
    llm_response = request(scoring_prompt).strip()
    
    try:
        llm_response = llm_response[llm_response.find('{'):llm_response.rfind('}')+1]  # Extract JSON part
        score = json.loads(llm_response)
        if not (0 <= score.get(section, 0) <= 100):
            raise ValueError("Invalid score range")
    except Exception as e:
        st.error(f"Error parsing score for section {section}: {e}")
        st.write("Raw response:", llm_response)  # Log response for debugging
        score = {section: 0}
    
    return score

def score_cv(cv_text, job_desc_text, selected_sections):
    """
    Scores each section individually and compiles the results.
    """
    scores = {}
    for section in selected_sections:
        scores.update(score_section(cv_text, job_desc_text, section))
    
    scores["avg_score"] = np.mean(list(scores.values())) if scores else 0
    return scores

def rank_cv_candidates(cv_entries, job_desc_text, selected_sections):
    """
    Scores each candidate individually and ranks them based on the selected criteria.
    """
    ranking_data = []
    for cv in cv_entries:
        scores = score_cv(cv["text"], job_desc_text, selected_sections)
        ranking_data.append({"name": cv["name"], "scores": scores, "avg_score": scores["avg_score"]})
    
    ranking_data = sorted(ranking_data, key=lambda x: x["avg_score"], reverse=True)
    return ranking_data

def display_radar_chart(ranking_data, selected_sections):
    """
    Displays a radar chart comparing candidates across selected sections.
    """
    if not ranking_data:
        st.warning("No ranking data available for radar chart.")
        return
    
    num_vars = len(selected_sections)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    for candidate in ranking_data:
        scores = [candidate["scores"].get(section, 0) for section in selected_sections]
        scores += scores[:1]  # Close the radar chart loop
        ax.plot(angles, scores, linewidth=2, linestyle='solid', label=candidate["name"])
        ax.fill(angles, scores, alpha=0.25)
    col1,col2 = st.columns(2)
    with col1:
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(selected_sections, fontsize=10)
        ax.set_yticklabels([])
        ax.set_title("Candidate Comparison by Selected Sections")
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        st.pyplot(fig)

def skill_ranker():
    st.title("CV Ranker with Radar Chart")
    
    # Upload job description
    job_desc_file = st.file_uploader("Upload Job Description (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    job_desc_text = ""
    
    if job_desc_file:
        if job_desc_file.type == "application/pdf":
            job_desc_text = extract_text_from_pdf(job_desc_file)
        elif job_desc_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            job_desc_text = extract_text_from_docx(job_desc_file)
        elif job_desc_file.type == "text/plain":
            job_desc_text = extract_text_from_txt(job_desc_file)
    
    # Upload CVs
    uploaded_files = st.file_uploader("Upload CVs (PDF, DOCX, or TXT)", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    cv_entries = []
    if uploaded_files:
        for file in uploaded_files:
            if file.type == "application/pdf":
                text = extract_text_from_pdf(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = extract_text_from_docx(file)
            elif file.type == "text/plain":
                text = extract_text_from_txt(file)
            
            name = extract_name(text)
            cv_entries.append({"filename": file.name, "text": text, "name": name})
    
    # Select sections for ranking
    selected_sections = st.multiselect("Select sections to evaluate",max_selections=5, options = ["Skills", "Education", "Experience", "Knowledge", "Projects", "Certifications", "Languages", "Leadership", "Publications", "Volunteer Work"])
    
    if st.button("Rank Candidates") and cv_entries and selected_sections:
        ranking_data = rank_cv_candidates(cv_entries, job_desc_text, selected_sections)
        display_radar_chart(ranking_data, selected_sections)
        
        # Display ranked candidates
        df = pd.DataFrame([{**{"Name": r["name"], "Average Score": r["avg_score"]}, **r["scores"]} for r in ranking_data])
        st.write("### Ranked Candidates")
        st.dataframe(df)
