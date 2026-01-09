# AI Exam Agent

An interactive AI agent that administers an oral exam to students based on their Python code and heuristics. The agent uses an ensemble of Large Language Models (LLMs) to generate questions, conduct the exam via audio and text, and evaluate the student's performance.

## Prerequisites
- Python 3.10+
- Microphone and Speakers
- **uv** (Package Manager)

## Installation

1.  Clone the repository and open your terminal in the project directory.
2.  Install dependencies using `uv`:
    ```bash
    uv sync
    ```

## Configuration

This project uses a `.env` file for configuration.
Create a `.env` file in the root directory (based on the example below) or rely on the UI to input keys manually.

**Example `.env`**:
```env
# Standard OpenAI
OPENAI_API_KEY="sk-..."

# Or Azure OpenAI
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_MODEL_NAME="gpt-4"
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"

# Optional Additional Providers
ANTHROPIC_API_KEY="sk-ant-..."
GOOGLE_API_KEY="AIza..."
```

## Running the App

1.  Run Streamlit via `uv`:
    ```bash
    uv run streamlit run app.py
    ```
2.  The app will open in your browser (usually `http://localhost:8501`).

## Usage Guide

1.  **Configuration (Sidebar)**:
    - The app will auto-detect API keys from `.env`.
    - Select "General Python" or "Custom" module.
    - If Custom, upload a text file with lecture notes.
2.  **Tab 1: Upload Data**:
    - Upload the Student's Python Code (`.py`).
    - Upload the Student's Heuristics text (`.txt`).
    - Click **Generate Questions**.
3.  **Tab 2: Oral Exam**:
    - Listen to the question (Click "Play Question").
    - **Record Answer**: Click "Record", speak your answer, and stop recording.
    - Verify the transcription and edit if needed.
    - Click "Submit Answer" to move to the next question.
4.  **Tab 3: Evaluation**:
    - After the exam finishes, click **Run Evaluation**.
    - View the detailed feedback aggregated from the available LLMs.

## Troubleshooting
- **Microphone**: Allow browser permission for the microphone.
- **Push Protection**: Verify `.env` is in `.gitignore` to avoid leaking secrets.
