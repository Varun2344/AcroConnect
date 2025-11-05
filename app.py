import streamlit as st
import google.generativeai as genai
import os
import sqlite3
from dotenv import load_dotenv

# --- 1. SETUP AND CONFIGURATION ---
load_dotenv()  # Load environment variables from .env file

# Configure the Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key not found. Please set it in your .env file.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

# Set page config
st.set_page_config(
    page_title="AcroConnect PoC",
    page_icon="🎓",
    layout="wide"
)

# --- 2. DATABASE SETUP ---
DB_FILE = "acroconnect.db"

def init_db():
    """Initializes the SQLite database and creates the 'students' table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        career_goal TEXT NOT NULL,
        python_skill INTEGER,
        sql_skill INTEGER
    );
    """)
    conn.commit()
    conn.close()

# Run the DB setup
init_db()

# --- 3. MULTI-PAGE NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Student Portal", "TPO Dashboard"])

if page == "Student Portal":
    st.title("🎓 AcroConnect - Student Portal")
    st.write("This is where students will build their profile and get AI-driven career advice.")
    # We will build the form here tomorrow

elif page == "TPO Dashboard":
    st.title("📊 AcroConnect - TPO Dashboard")
    st.write("This is the secure area for the TPO to view analytics and student data.")
    # We will build the TPO view here tomorrow