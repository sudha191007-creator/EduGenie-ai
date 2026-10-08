# EduGenie - Google Gemini Powered Learning Assistant

Built from the supplied EduGenie documentation. Features: Q&A, concept explanation, 3-question MCQ quiz, summary, personalized learning path, FastAPI APIs, responsive frontend, Swagger docs and health check.

## Windows CMD

py --version
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env

Add your real Gemini key to `.env`:
GEMINI_API_KEY=YOUR_REAL_KEY

Run:
python -m uvicorn app.main:app --reload

Open http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health

The supplied document refers to Gemini 1.5 Pro and LaMini-Flan-T5. This implementation uses the current Google GenAI SDK with configurable Gemini models and fallbacks. The local LaMini path is intentionally optional because it requires a large model download.
