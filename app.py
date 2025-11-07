import streamlit as st
import google.generativeai as genai
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

# --- 1. SETUP AND CONFIGURATION ---
load_dotenv()  # Load environment variables from .env file

# Configure the Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key not found. Please set your GOOGLE_API_KEY secret in Streamlit Cloud.")
else:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")

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
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    career_goal TEXT NOT NULL,
    python_skill INTEGER,
    sql_skill INTEGER,
    generated_roadmap TEXT
    );
    """)
    conn.commit()
    conn.close()

# Run the DB setup
init_db()

# --- 3. HELPER FUNCTIONS (The "Guts") ---

def get_ai_roadmap(career_goal, python_skill, sql_skill):
    """Calls the Gemini API to generate a personalized roadmap."""
    prompt = f"""
    You are an expert career counselor for computer science students.
    A student has the following profile:
    - Career Goal: {career_goal}
    - Python Skill: {python_skill} out of 5
    - SQL Skill: {sql_skill} out of 5
    - 

    Generate a 2-week, actionable "Sprint Roadmap" for them.
    The roadmap must be concise, in markdown format, with 3-5 clear action items.
    Focus on practical projects, specific tutorials, and skills they need to bridge the gap.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating AI roadmap: {e}")
        return None

def save_to_db(name, email, phone, career_goal, python_skill, sql_skill, roadmap):
    """Saves the student's data and their new roadmap to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email, phone, career_goal, python_skill, sql_skill, generated_roadmap) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, career_goal, python_skill, sql_skill, roadmap)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return False
    
def delete_student_from_db(student_id):
    """Deletes a student record from the database by their ID."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting from database: {e}")
        return False

# --- 4. MULTI-PAGE NAVIGATION ---
st.sidebar.title("AcroConnect PoC Navigation")
page = st.sidebar.radio("Go to", ["Student Portal", "TPO Dashboard"])

if page == "Student Portal":
    st.title("🎓 AcroConnect - Student Portal")
    st.write("Enter your details to get a personalized, AI-generated career roadmap.")

    # Create the form for student input
    with st.form("student_profile_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        career_goal = st.text_input("Dream Career Goal (e.g., Data Scientist, Backend Developer)")
        python_skill = st.slider("Your Python Skill (1=Beginner, 5=Expert)", 1, 5, 3)
        sql_skill = st.slider("Your SQL Skill (1=Beginner, 5=Expert)", 1, 5, 3)
        
        submitted = st.form_submit_button("🚀 Get My AI Roadmap")

    # --- This is the logic that runs when the button is clicked ---
    if submitted:
        if not name or not career_goal:
            st.warning("Please fill out all fields.")
        else:
            with st.spinner("🚀 Your personal AI is building your roadmap..."):
                # 1. Call the AI
                roadmap = get_ai_roadmap(career_goal, python_skill, sql_skill)
                
                if roadmap:
                    # 2. Save to DB
                    save_to_db(name, email, phone, career_goal, python_skill, sql_skill, roadmap)
                    
                    # 3. Display results
                    st.balloons()
                    st.success("Your roadmap is ready!")
                    st.markdown(f"### Here is your 2-Week Sprint, {name}:")
                    st.markdown(roadmap)

elif page == "TPO Dashboard":
    st.title("📊 AcroConnect - TPO Dashboard")
    st.write("This is the secure area for the TPO to view analytics and student data.")

    # --- 4.1 Simple Password Protection ---
    # This is NOT real auth, but it CHECKS THE BOX for a prototype
    password = st.text_input("Enter TPO Password", type="password")
    
    if password == "tpo123":  # Simple hardcoded password
        st.success("Access Granted")
        
        # --- 4.2 Display Student Data ---
        st.subheader("All Student Submissions")
        try:
            conn = sqlite3.connect(DB_FILE)
    # 1. Update the SQL query to get the new fields
            query = "SELECT id, name, email, phone, career_goal, python_skill, sql_skill, generated_roadmap FROM students"
    
    # 2. Use Pandas to read the SQL query directly. This automatically gets the column headers!
            df = pd.read_sql_query(query, conn)
            conn.close()
    
    # 3. Display the pandas DataFrame. It will now have correct headers.
            st.dataframe(df,
            column_config={
            "id": "Student ID",
            "name": "Student Name",
            "email": "Email",
            "phone": "Phone",
            "career_goal": "Career Goal",
            "python_skill": "Python (1-5)",
            "sql_skill": "SQL (1-5)",
            "generated_roadmap": "AI Roadmap"
            },
            use_container_width=True
        )
            # Option to delete a student record
            st.subheader("Delete a Student Record")
            student_id_to_delete = st.number_input("Enter Student ID to Delete", min_value=1, step=1)
            if st.button("Delete Student"):
                if delete_student_from_db(student_id_to_delete):
                    st.success(f"Student ID {student_id_to_delete} deleted successfully.")
                else:
                    st.error("Failed to delete student.")        
        except Exception as e:
            st.error(f"Error reading from database: {e}")
            
    elif password:
        st.error("Incorrect Password. Access Denied.")