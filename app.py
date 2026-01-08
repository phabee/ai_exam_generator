import streamlit as st
import os
from src.llm_manager import OpenAIProvider, AnthropicProvider, GoogleProvider, EnsembleEvaluator
from src.exam_flow import QuestionGenerator, ExamSession
from src.context_manager import ContextManager
from src.audio_manager import AudioManager

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="AI Oral Exam Agent", page_icon="🎓")

# Session State Initialization
if "exam_session" not in st.session_state:
    st.session_state.exam_session = ExamSession()
if "context_manager" not in st.session_state:
    st.session_state.context_manager = ContextManager()
if "audio_manager" not in st.session_state:
    st.session_state.audio_manager = AudioManager()
if "llm_provider" not in st.session_state:
    # Try to auto-initialize if env vars exist
    if os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"):
         st.session_state.llm_provider = OpenAIProvider()
    else:
        st.session_state.llm_provider = None

def main():
    st.title("🎓 AI Oral Exam Agent")

    # Sidebar: Configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Check if we have a provider
        if st.session_state.llm_provider:
            st.success("✅ AI Model Configured (Env)")
        else:
            st.warning("No API Keys found in .env")
            # API Keys Manual Entry (Fallback)
            openai_key = st.text_input("OpenAI API Key", type="password")
            anthropic_key = st.text_input("Anthropic API Key", type="password")
            google_key = st.text_input("Google API Key", type="password")
            
            if st.button("Initialize Agents"):
                if openai_key:
                    st.session_state.llm_provider = OpenAIProvider(openai_key)
                    st.success("Agents Initialized!")

        st.divider()
        
        # Module Selection
        module_name = st.selectbox("Select Module", ["General Python", "Data Science", "Custom"])
        context_text = ""
        if module_name == "Custom":
            uploaded_context = st.file_uploader("Upload Lecture/Topic Context (txt)", type=["txt"])
            if uploaded_context:
                context_text = uploaded_context.read().decode("utf-8")
        
        if st.button("Set Context"):
            st.session_state.context_manager.load_module_context(module_name, context_text)
            st.success(f"Context set for {module_name}")

    # Main Area
    if not st.session_state.llm_provider:
        st.info("👈 Please configure API keys in the sidebar to start.")
        return

    # Tabs for Phases
    tab1, tab2, tab3 = st.tabs(["1. Upload Data", "2. Oral Exam", "3. Evaluation"])

    with tab1:
        st.header("Student Submission")
        col1, col2 = st.columns(2)
        with col1:
            code_file = st.file_uploader("Upload Python Code (.py)", type=["py"])
        with col2:
            heuristics_file = st.file_uploader("Upload Heuristics (.txt)", type=["txt"])

        if code_file and heuristics_file:
            code_text = code_file.read().decode("utf-8")
            heuristics_text = heuristics_file.read().decode("utf-8")
            
            if st.button("Generate Questions"):
                with st.spinner("Analyzing code and generating questions..."):
                    q_gen = QuestionGenerator(st.session_state.llm_provider)
                    questions = q_gen.generate_questions(code_text, heuristics_text, st.session_state.context_manager)
                    st.session_state.exam_session.start_exam(questions)
                    st.success("Questions Generated! Proceed to 'Oral Exam' tab.")

    with tab2:
        st.header("Oral Examination")
        
        if not st.session_state.exam_session.questions:
            st.warning("Please generate questions first.")
        elif st.session_state.exam_session.is_finished():
            st.success("Exam Finished! Proceed to 'Evaluation' tab.")
            st.write(st.session_state.exam_session.get_transcript_text())
        else:
            current_q = st.session_state.exam_session.get_current_question()
            st.subheader(f"Question {st.session_state.exam_session.current_question_index + 1}")
            st.info(current_q)
            
            # Text-to-Speech
            if st.button("🔊 Play Question"):
                audio_path = st.session_state.audio_manager.text_to_speech(current_q)
                if audio_path:
                    st.audio(audio_path)
            
            # Audio Answer
            audio_answer = st.audio_input("Record your answer")
            if audio_answer:
                with st.spinner("Transcribing..."):
                    transcription = st.session_state.audio_manager.speech_to_text(audio_answer)
                    st.info(f"Transcribed: {transcription}")
                    # Allow user to edit or confirm
                    answer = st.text_area("Confirm/Edit Answer:", value=transcription, height=100)
            else:
                answer = st.text_area("Your Answer (Text):", height=100)
            
            if st.button("Submit Answer"):
                if answer:
                    st.session_state.exam_session.record_answer(answer)
                    st.rerun()
                else:
                    st.warning("Please provide an answer.")

    with tab3:
        st.header("Final Evaluation")
        if not st.session_state.exam_session.is_finished():
            st.info("Complete the exam to see the evaluation.")
        else:
            if st.button("Run Evaluation"):
                transcript = st.session_state.exam_session.get_transcript_text()
                
                # Setup Providers - if we have a main one, reuse it or check envs
                providers = []
                
                # Add the main provider if it exists
                if st.session_state.llm_provider:
                    providers.append(st.session_state.llm_provider)
                
                # Check for others if keys were manually provided (skip for now to respect "single model" request mostly)
                # But we can check envs for other providers just in case
                if os.getenv("ANTHROPIC_API_KEY"):
                    providers.append(AnthropicProvider(os.getenv("ANTHROPIC_API_KEY")))
                if os.getenv("GOOGLE_API_KEY"):
                    providers.append(GoogleProvider(os.getenv("GOOGLE_API_KEY")))
                
                if not providers:
                    st.error("No providers available for evaluation.")
                else:
                    evaluator = EnsembleEvaluator(providers)
                    with st.spinner("Consulting the examiner..."):
                        # In a real app, we'd pass code/heuristics too
                        results = evaluator.evaluate(transcript, system_prompt="Evaluate this student's oral exam performance based on the transcript.")
                        summary = evaluator.aggregate_feedback(results)
                        st.markdown(summary)

if __name__ == "__main__":
    main()
