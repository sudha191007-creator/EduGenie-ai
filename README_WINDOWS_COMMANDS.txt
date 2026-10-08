EDUGENIE - COPY/PASTE COMMANDS

py --version
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env

Put your real key in .env, save it, then:
python -m uvicorn app.main:app --reload

Browser: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health

Next time:
venv\Scripts\activate
python -m uvicorn app.main:app --reload

Stop: Ctrl+C
