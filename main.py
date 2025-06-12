from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import speech_recognition as sr
from pydub import AudioSegment
from sql_generator import SQLGenerator
from openai_helper import summarize_db_results
from xampp import run_query

import uuid
import os
import datetime
import re
import traceback
import codecs
# import pyttsx3  # ❌ Disabled for Render (no audio device)

# --- Utility Functions ---

def safe_strip(value):
    return str(value).strip().lower() if value is not None else ''

def remove_duplicates_safely(db_results):
    seen_keys = set()
    unique_results = []
    for row in db_results:
        name = safe_strip(row[0]) if len(row) > 0 else ''
        location = safe_strip(row[1]) if len(row) > 1 else ''
        url = safe_strip(row[4]) if len(row) > 4 else ''
        key = (name, location, url)
        if key not in seen_keys:
            seen_keys.add(key)
            unique_results.append(row)
    return unique_results

def insert_current_year(text):
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    month_to_number = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    # Range dates like "March 2nd to 4th"
    range_pattern = r'\b(' + '|'.join(month_to_number) + r')\s+(\d{1,2})(st|nd|rd|th)?\s+(to|-)\s+(\d{1,2})(st|nd|rd|th)?\b'
    def add_year_to_range(match):
        month_str = match.group(1)
        start_day = match.group(2)
        end_day = match.group(5)
        month_num = month_to_number[month_str]
        year = current_year if month_num >= current_month else current_year + 1
        return f"{month_str} {start_day} {year} to {month_str} {end_day} {year}"
    text = re.sub(range_pattern, add_year_to_range, text)

    # "first week of April"
    week_pattern = r'\b(first|second|third|fourth)\s+week\s+of\s+(' + '|'.join(month_to_number) + r')\b'
    week_start_day = {'first': 1, 'second': 8, 'third': 15, 'fourth': 22}
    def add_year_to_week(match):
        week = match.group(1).lower()
        month_str = match.group(2)
        month_num = month_to_number[month_str]
        start = week_start_day[week]
        end = start + 6
        year = current_year if month_num >= current_month else current_year + 1
        return f"{month_str} {start} {year} to {month_str} {end} {year}"
    text = re.sub(week_pattern, add_year_to_week, text, flags=re.IGNORECASE)

    # "July 5th"
    single_pattern = r'\b(' + '|'.join(month_to_number) + r')\s+(\d{1,2})(st|nd|rd|th)?\b'
    def add_year_to_single(match):
        month_str = match.group(1)
        day = match.group(2)
        month_num = month_to_number[month_str]
        year = current_year if month_num >= current_month else current_year + 1
        return f"{month_str} {day} {year}"
    text = re.sub(single_pattern, add_year_to_single, text)
    
    return text

# --- FastAPI Setup ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join("static", "index.html"))

# --- Voice Transcription Endpoint ---

def convert_audio_to_wav(file, target_path):
    audio = AudioSegment.from_file(file)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(target_path, format="wav")

def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source, duration=5)
    try:
        return recognizer.recognize_google(audio) # type: ignore
    except sr.UnknownValueError:
        return "UNRECOGNIZED_AUDIO"
    except sr.RequestError as e:
        return f"SPEECH_API_ERROR: {e}"

# def speak_text(text):
#     try:
#         engine = pyttsx3.init()
#         engine.setProperty('rate', 150)
#         engine.setProperty('volume', 1.0)
#         engine.say(text)
#         engine.runAndWait()
#     except Exception as e:
#         print("🗣 TTS Error:", str(e))

@app.post("/transcribe-voice/")
async def transcribe_voice(file: UploadFile = File(...)):
    temp_filename = f"{uuid.uuid4()}.wav"
    try:
        await file.seek(0)
        convert_audio_to_wav(file.file, temp_filename)
        text = speech_to_text(temp_filename)
        print("📝 Transcribed:", text)

        # speak_text(text)  # Disabled in cloud

        return { "success": True, "text": text }

    except Exception as e:
        traceback_str = traceback.format_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e), "details": traceback_str})

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# --- Text Processing Endpoint ---

@app.post("/process-text/")
async def process_text(text: str = Form(...)):
    try:
        processed_text = insert_current_year(text)
        generator = SQLGenerator()
        result = generator.generate_query(processed_text)

        if result["success"]:
            sql_query = codecs.decode(result["query"], 'unicode_escape')
            db_results = run_query(sql_query)
            db_results_cleaned = remove_duplicates_safely(db_results)
            summary = summarize_db_results(text, db_results_cleaned)

            return {
                "success": True,
                "query": sql_query,
                "results": db_results_cleaned,
                "summary": summary
            }

        return {
            "success": False,
            "error": result["error"]
        }

    except Exception as e:
        traceback_str = traceback.format_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e), "details": traceback_str})
