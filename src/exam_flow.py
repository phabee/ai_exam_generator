from typing import List, Dict
from .llm_manager import LLMProvider, EnsembleEvaluator
from .context_manager import ContextManager

class QuestionGenerator:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def generate_questions(self, code: str, heuristics: str, context_manager: ContextManager) -> List[str]:
        context_prompt = context_manager.get_system_prompt_addition()
        system_prompt = f"You are a strict professor conducting an oral exam.{context_prompt}"
        user_prompt = f"""
        Student Code:
        {code}

        Student Heuristics:
        {heuristics}

        Generate 3 challenging questions. 
        1. One specific to the code implementation.
        2. One about the heuristics/design choices.
        3. One about the fundamental theory related to the module context.
        
        Return the questions as a Python list of strings.
        """
        response = self.llm.generate_response(system_prompt, user_prompt)
        # Simplified parsing for now
        return [q.strip() for q in response.split('\n') if '?' in q][:3]

class ExamSession:
    def __init__(self):
        self.questions = []
        self.current_question_index = 0
        self.transcript = []

    def start_exam(self, questions: List[str]):
        self.questions = questions
        self.current_question_index = 0
        self.transcript = []

    def get_current_question(self) -> str:
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def record_answer(self, answer_text: str):
        current_q = self.get_current_question()
        if current_q:
            self.transcript.append({"question": current_q, "answer": answer_text})
            self.current_question_index += 1

    def is_finished(self) -> bool:
        return self.current_question_index >= len(self.questions)

    def get_transcript_text(self) -> str:
        text = "Exam Transcript:\n"
        for entry in self.transcript:
            text += f"Q: {entry['question']}\n\nA: {entry['answer']}\n\n---\n"
        return text
