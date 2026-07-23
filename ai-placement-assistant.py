import streamlit as st
from pypdf import PdfReader
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os

# Set page configuration
st.set_page_config(page_title="AI Placement & Mock Interview App", page_icon="🎙️", layout="wide")

st.title("🎙️ AI-Driven Placement & Interview Evaluation Hub")
st.markdown("Scan resumes against standard applicant models, run mock test loops, and view complete analytics.")

# --- PERSISTENT STATE INITIALIZATION ---
if "interview_question" not in st.session_state:
    st.session_state.interview_question = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = ""

# --- SIDEBAR CONFIGURATION & SECURITY ---
st.sidebar.title("🧭 Configuration & Navigation")

# Fix 1: Secure API Key Input (No hardcoding, safe from accidental exposure)
user_groq_key = st.sidebar.text_input("Enter Groq API Key:", type="password", help="Get a free key from console.groq.com")
if user_groq_key:
    os.environ["GROQ_API_KEY"] = user_groq_key#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

app_mode = st.sidebar.radio("Go to Module:", ["ATS Screening", "Interactive Mock Loop"])

# Global check to help guide the user if they forget the key
if not user_groq_key:
    st.warning("🔑 Please enter your Groq API Key in the left sidebar configuration panel to unlock system modules.")

# Helper function to parse PDF structures cleanly
def parse_resume_document(file_buffer):
    pdf_reader = PdfReader(file_buffer)
    extracted_raw_text = ""
    for target_page in pdf_reader.pages:
        page_text = target_page.extract_text()
        if page_text:
            extracted_raw_text += page_text + "\n"
    return extracted_raw_text

# --- PILLAR 1: ATS SCREENING SYSTEM ---
if app_mode == "ATS Screening":
    st.header("📄 Automated Applicant Profile Matcher")
    st.caption("Upload your resume and the target job description to evaluate your profile layout alignment.")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_pdf = st.file_uploader("Upload Profile Document (PDF Format Only)", type=["pdf"])
    with col2:
        job_details = st.text_area("Paste Target Job Description Requirement Matrix:", height=200)

    # Fix 2: Wrap action inside action triggers to prevent error rendering on load
    if st.button("🔍 Execute ATS Matrix Alignment Analysis"):
        if not user_groq_key:
            st.error("❌ Action Blocked: Provide a valid Groq API Key in the sidebar configuration matrix first.")
        elif not uploaded_pdf or not job_details:
            st.error("❌ Action Blocked: Ensure both your profile PDF and the target Job Description text areas are populated.")
        else:
            with st.spinner("Parsing text files and executing LLM validation schema..."):
                try:
                    resume_parsed_text = parse_resume_document(uploaded_pdf)
                    
                    # Core strict model declaration (Low temperature for accurate mapping logic)
                    strict_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
                    ats_prompt = ChatPromptTemplate.from_messages([
                        ("system", (
                            "You are an expert technical recruiter analyzing a candidate's file against operational criteria.\n"
                            "Return a strict JSON format with these exact string keys:\n"
                            "- 'match_score': integer value between 0 and 100\n"
                            "- 'missing_tech_keywords': a bulleted text string list of critical requirements missing\n"
                            "- 'resume_reconstruction_advice': quick bullet points on how to restructure sections."
                        )),
                        ("human", "RESUME CONTENT:\n{resume}\n\nJOB REQUIREMENTS:\n{jd}")
                    ])
                    
                    eval_chain = ats_prompt | strict_llm | JsonOutputParser()
                    analysis_payload = eval_chain.invoke({"resume": resume_parsed_text, "jd": job_details})
                    
                    st.success("✅ Analysis Execution Complete")
                    st.metric(label="Calculated ATS System Alignment Match", value=f"{analysis_payload['match_score']}%")
                    
                    st.subheader("❌ Detected Keyword Skill Gaps")
                    st.write(analysis_payload['missing_tech_keywords'])
                    
                    st.subheader("💡 Strategic Profile Optimization Tips")
                    st.write(analysis_payload['resume_reconstruction_advice'])
                except Exception as e:
                    st.error(f"⚠️ Infrastructure Engine Error: {str(e)}")

# --- PILLAR 2: MOCK INTERVIEW EVALUATION ---
elif app_mode == "Interactive Mock Loop":
    st.header("🤖 Adaptive Domain Technical Interview Core")
    st.caption("Select your target role path and type your answer to get graded.")
    
    # Pre-populate UI text area with session state value if it exists to maintain layout continuity
    role_input = st.text_input("Enter Target Professional Sub-Domain:", 
                               value=st.session_state.target_role,
                               placeholder="e.g., Backend Developer, Data Analyst Intern, Financial Controller")
    
    if st.button("🎲 Generate Technical Interview Prompt"):
        if not user_groq_key:
            st.error("❌ Action Blocked: Provide a valid Groq API Key in the sidebar configuration matrix first.")
        elif not role_input:
            st.error("❌ Missing Field: Please explicitly detail a target role profile first.")
        else:
            # Fix 3 & 4: Bind the input to session state immediately and apply generic domain prompting
            st.session_state.target_role = role_input
            with st.spinner("Formulating structural question metrics..."):
                try:
                    creative_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
                    q_prompt = ChatPromptTemplate.from_messages([
                        ("system", (
                            "You are an expert interviewer and industry veteran specializing in the field of {role}.\n"
                            "Ask a single challenging, highly relevant conceptual or situational interview question customized specifically for a {role} position.\n"
                            "Do not include greeting text, conversational fluff, or introductory sentences. Output only the question."
                        )),
                        ("human", "Generate the interview question prompt now.")
                    ])
                    question_chain = q_prompt | creative_llm
                    st.session_state.interview_question = question_chain.invoke({"role": st.session_state.target_role}).content
                except Exception as e:
                    st.error(f"⚠️ Infrastructure Engine Error: {str(e)}")

    # Visual container separation block
    if st.session_state.interview_question:
        st.info(f"### ❓ Question Context for {st.session_state.target_role}:\n{st.session_state.interview_question}")
        candidate_response = st.text_area("Type your comprehensive solution response below:", height=150)
        
        if st.button("📊 Submit Response for Evaluation Grading"):
            if not user_groq_key:
                st.error("❌ Action Blocked: Provide a valid Groq API Key in the sidebar configuration matrix first.")
            elif not candidate_response:
                st.error("❌ Missing Answer Text: Please type your response inside the solution dashboard workspace before execution tracking.")
            else:
                with st.spinner("Analyzing response syntax and semantic patterns..."):
                    try:
                        strict_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
                        eval_prompt = ChatPromptTemplate.from_messages([
                            ("system", (
                                "You are a strict technical evaluator checking domain competence responses.\n"
                                "Return a strict JSON map layout with these keys:\n"
                                "- 'score': integer out of 100\n"
                                "- 'technical_strengths': what concepts they hit correctly\n"
                                "- 'logical_flaws': bugs, structural edge cases, or concept errors in their logic\n"
                                "- 'reference_response': an optimized structural reference answer detailing how to score a perfect 100."
                            )),
                            ("human", "Question Prompt: {question}\nCandidate Answer: {answer}\nTarget Domain: {role}")
                        ])
                        
                        grading_chain = eval_prompt | strict_llm | JsonOutputParser()
                        
                        # Fix 3: Passed persistent session state safely to the prompt parameter matrix
                        grading_output = grading_chain.invoke({
                            "question": st.session_state.interview_question,
                            "answer": candidate_response,
                            "role": st.session_state.target_role
                        })
                        
                        st.success("🏁 Grading Process Complete")
                        st.metric("Performance Grade", f"{grading_output['score']}/100")
                        
                        st.subheader("🎯 Identified Analytical Strengths")
                        st.write(grading_output['technical_strengths'])
                        
                        st.subheader("⚠️ Logical Flaws & Conceptual Gaps")
                        st.write(grading_output['logical_flaws'])
                        
                        st.subheader("📚 High-Performance Reference Model Answer")
                        st.code(grading_output['reference_response'], language="markdown")
                    except Exception as e:
                        st.error(f"⚠️ Processing Parse Error: {str(e)}")