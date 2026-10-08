from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
import os, json, re

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")

KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

FALLBACK = [
    x.strip()
    for x in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.5-flash-lite,gemini-2.5-flash"
    ).split(",")
    if x.strip()
]

client = None


def ai(prompt, json_mode=False):
    global client

    if not KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add your key to .env."
        )

    if client is None:
        client = genai.Client(api_key=KEY)

    last = None

    for model in [MODEL] + [m for m in FALLBACK if m != MODEL]:
        try:
            cfg = (
                {"response_mime_type": "application/json"}
                if json_mode
                else None
            )

            r = client.models.generate_content(
                model=model,
                contents=prompt,
                config=cfg
            )

            if getattr(r, "text", None):
                return r.text.strip()

        except Exception as e:
            last = e

    raise RuntimeError(f"Gemini request failed. Last error: {last}")


def clean_json(s):
    s = re.sub(
        r"^```(?:json)?\s*",
        "",
        s.strip(),
        flags=re.I
    )

    s = re.sub(r"\s*```$", "", s)

    return s


def call(fn, *args):
    try:
        return fn(*args)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=str(e)
        )


def qa(x):
    return ai(
        f"""You are EduGenie, an academic tutor.

Answer this question clearly and accurately:

{x}

Give the direct answer first, then a concise explanation and example when useful.
Do not invent citations."""
    )


def explain(x):
    return ai(
        f"""Explain this educational topic to a beginner:

{x}

Use:
- One-line definition
- Simple explanation
- 2-4 key points
- One analogy/example
- Short Remember section."""
    )


def summary(x):
    return ai(
        f"""Summarize this educational passage:

{x}

Return:
- Short summary
- 4-7 key points
- One-line Quick Revision section

Preserve important meaning."""
    )


def path(topic, level):
    return ai(
        f"""Create a realistic learning path for {topic}
for a {level} learner.

Sections:
- Learning Goal
- Foundations
- Core Concepts
- Practice
- Advanced Topics
- Timeline
- Projects/Activities
- Resource Types

Do not invent specific URLs."""
    )


def quiz(x):
    raw = clean_json(
        ai(
            f"""Create exactly 3 MCQs from this educational content:

{x}

Return ONLY JSON:

{{
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "exact correct option text",
      "explanation": "short explanation"
    }}
  ]
}}

Exactly 3 questions.
Exactly 4 options each.
One correct answer.
All questions must be answerable from the content.""",
            True
        )
    )

    data = json.loads(raw)

    if len(data.get("questions", [])) != 3:
        raise RuntimeError(
            "Quiz did not contain exactly 3 questions."
        )

    for q in data["questions"]:
        if (
            len(q.get("options", [])) != 4
            or q.get("answer") not in q["options"]
        ):
            raise RuntimeError(
                "Invalid quiz format returned by Gemini."
            )

    return data


app = FastAPI(
    title="EduGenie - Gemini Powered Learning Assistant",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory=ROOT / "static"),
    name="static"
)


templates = Jinja2Templates(
    directory=ROOT / "templates"
)


class TextReq(BaseModel):
    text: str = Field(
        min_length=2,
        max_length=30000
    )


class LearnReq(BaseModel):
    topic: str = Field(
        min_length=2,
        max_length=500
    )
    level: str = "Beginner"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "EduGenie"
    }


@app.post("/qa")
def api_qa(r: TextReq):
    return {
        "result": call(qa, r.text)
    }


@app.post("/explain")
def api_explain(r: TextReq):
    return {
        "result": call(explain, r.text)
    }


@app.post("/summarize")
def api_summary(r: TextReq):
    return {
        "result": call(summary, r.text)
    }


@app.post("/quiz")
def api_quiz(r: TextReq):
    return call(quiz, r.text)


@app.post("/learn/recommendations")
def api_path(r: LearnReq):
    return {
        "result": call(
            path,
            r.topic,
            r.level
        )
    }