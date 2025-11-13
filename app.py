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
        model = genai.GenerativeModel('gemini-1.0-pro')
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
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create the students table with the new 'communication_skill'
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        career_goal TEXT NOT NULL,
        python_skill INTEGER,
        sql_skill INTEGER,
        communication_skill INTEGER, 
        generated_roadmap TEXT
    );
    """)
    # Create the jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT,
        description TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

# Run the DB setup
init_db()

# --- 3. HELPER FUNCTIONS ---

def get_ai_roadmap(career_goal, python_skill, sql_skill, comm_skill):
    """Calls the Gemini API to generate a personalized roadmap."""
    # NEW: Added comm_skill to the prompt
    prompt = f"""
    You are an expert career counselor. A student has this profile:
    - Career Goal: {career_goal}
    - Python Skill: {python_skill}/5
    - SQL Skill: {sql_skill}/5
    - Communication Skill: {comm_skill}/5

    Generate a 2-week, actionable "Sprint Roadmap" for them in markdown.
    Focus on 3-5 practical action items. 
    **Must include at least one action item for improving their Communication skill.**
    """
    try:
        model = genai.GenerativeModel('gemini-1.0-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating AI roadmap: {e}")
        return None

def save_to_db(name, email, phone, career_goal, python_skill, sql_skill, comm_skill, roadmap):
    """Saves the student's data to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # NEW: Added communication_skill to the INSERT query
        cursor.execute(
            "INSERT INTO students (name, email, phone, career_goal, python_skill, sql_skill, communication_skill, generated_roadmap) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, email, phone, career_goal, python_skill, sql_skill, comm_skill, roadmap)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return False
        
def delete_student_from_db(student_id):
    """Deletes a student record by ID."""
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

def post_new_job(title, company, desc):
    """Saves a new job posting to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jobs (title, company, description) VALUES (?, ?, ?)",
            (title, company, desc)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error posting job: {e}")
        return False

def get_all_jobs():
    """Retrieves all job postings from the database."""
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT title, company, description FROM jobs ORDER BY job_id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- 4. MULTI-PAGE NAVIGATION ---
st.sidebar.title("AcroConnect PoC Navigation")
page = st.sidebar.radio("Go to", ["Home", "Student Portal", "TPO Dashboard"])


# --- 5. HOME PAGE ---
if page == "Home":
    st.title("Welcome to AcroConnect 🎓")
    st.markdown("### The AITR Placement Readiness Platform")
    st.write("") 
    st.subheader("About This Project (Proof of Concept)")
    st.write(
        """
        This is the 100% implemented Proof of Concept (PoC) for the AcroConnect Major Project.
        This PoC demonstrates the **complete, end-to-end data pipelines** which are the
        foundation for the entire 8th-semester application.
        """
    )
    st.subheader("Explore the PoC Features:")
    st.markdown(
        """
        * **Go to the ➡️ Student Portal:**
            * Fill out the form to get a personalized AI-generated career roadmap.
            * View all open job postings from the TPO.
            * This demonstrates the **Student-facing read/write** capabilities.

        * **Go to the ➡️ TPO Dashboard:**
            * Enter the password (`tpo123`) to access the secure admin view.
            * View live analytics, see all student data, and delete records.
            * Post new job openings that will instantly appear for students.
            * This demonstrates the **Admin-facing read/write** capabilities.
        """
    )

# --- 6. STUDENT PORTAL PAGE ---
elif page == "Student Portal":
    st.title("🎓 AcroConnect - Student Portal")
    
    # --- NEW: UI/UX Change ---
    with st.container(border=True):
        st.subheader("Get Your Personalized AI Roadmap")
        st.write("Fill out your profile below. Our AI will generate a custom 2-week sprint plan to help you reach your goals.")
        with st.form("student_profile_form"):
            
            # --- Personal Info Section ---
            st.markdown("##### 1. Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *", help="Your full name")
            with col2:
                email = st.text_input("Email Address *", help="Your college email")
            phone = st.text_input("Phone Number", help="Your contact number")

            # --- Career Goal Section ---
            st.markdown("##### 2. Career Goals")
            career_goal = st.text_input("Dream Career Goal *", "Data Scientist", help="e.g., Data Scientist, Backend Developer, UI/UX Designer")

            # --- Skills Section ---
            st.markdown("##### 3. Current Skill Assessment")
            col1, col2, col3 = st.columns(3)
            with col1:
                python_skill = st.slider("Python Skill (1-5)", 1, 5, 3)
            with col2:
                sql_skill = st.slider("SQL Skill (1-5)", 1, 5, 3)
            with col3:
                # --- NEW: Added Communication Skill ---
                comm_skill = st.slider("Communication Skill (1-5)", 1, 5, 3)
            
            submitted = st.form_submit_button("🚀 Get My AI Roadmap")

        if submitted:
            if not name or not career_goal or not email:
                st.warning("Please fill out all required (*) fields.")
            else:
                with st.spinner("🚀 Your personal AI is building your roadmap..."):
                    # --- NEW: Pass comm_skill to the AI and DB ---
                    roadmap = get_ai_roadmap(career_goal, python_skill, sql_skill, comm_skill)
                    if roadmap:
                        save_to_db(name, email, phone, career_goal, python_skill, sql_skill, comm_skill, roadmap)
                        st.balloons()
                        st.success("Your roadmap is ready!")
                        st.markdown(f"### Here is your 2-Week Sprint, {name}:")
                        st.markdown(roadmap)

    # --- NEW: UI/UX Change (Divider) ---
    st.divider()
    
    st.subheader("📢 View Open Job Postings")
    st.write("See all jobs posted by the TPO.")
    
    jobs_df = get_all_jobs()
    if jobs_df.empty:
        st.info("No jobs posted yet. Check back soon!")
    else:
        # --- NEW: UI/UX Change (Container) ---
        with st.container(height=300): # Makes this section scrollable
            for index, row in jobs_df.iterrows():
                with st.expander(f"**{row['title']}** at **{row['company']}**"):
                    st.markdown(row['description'])

# --- 7. TPO DASHBOARD PAGE ---
elif page == "TPO Dashboard":
    st.title("📊 AcroConnect - TPO Dashboard")
    st.write("Secure area for TPO to view analytics and manage data.")

    password = st.text_input("Enter TPO Password", type="password")
    
    if password == "tpo123":
        st.success("Access Granted")
        
        try:
            conn = sqlite3.connect(DB_FILE)
            # --- NEW: Get all columns including communication_skill ---
            query = "SELECT id, name, email, phone, career_goal, python_skill, sql_skill, communication_skill FROM students"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # --- TPO ANALYTICS ---
            # --- NEW: UI/UX Change (Container) ---
            with st.container(border=True):
                st.subheader("Live Analytics Dashboard")
                st.write("This dashboard updates in real-time as students submit their profiles.")
    
                if not df.empty:
                    # --- Chart 1: Skill Distribution ---
                    st.markdown("#### Student Skill Distribution")
                    # --- NEW: Add comm_skill to the chart ---
                    skill_dist_df = pd.DataFrame({
                        'Python': df['python_skill'].value_counts(),
                        'SQL': df['sql_skill'].value_counts(),
                        'Communication': df['communication_skill'].value_counts()
                    }).fillna(0).sort_index()
                    st.bar_chart(skill_dist_df, use_container_width=True)
    
                    # --- Chart 2: Average Skill Comparison ---
                    st.markdown("#### Average Skill Comparison")
                    # --- NEW: Add comm_skill to the chart ---
                    avg_skill_df = pd.DataFrame({
                        'Average Skill Level': [df['python_skill'].mean(), df['sql_skill'].mean(), df['communication_skill'].mean()]
                    }, index=['Python', 'SQL', 'Communication'])
                    st.bar_chart(avg_skill_df, use_container_width=True)
                else:
                    st.info("No student data to display analytics. Submit a student in the Student Portal.")

            # --- TPO STUDENT TABLE ---
            st.subheader("All Student Submissions")
            st.dataframe(df,
                column_config={
                    "id": "Student ID",
                    "name": "Student Name",
                    "email": "Email",
                    "phone": "Phone",
                    "career_goal": "Career Goal",
                    "python_skill": "Python (1-5)",
                    "sql_skill": "SQL (1-5)",
                    "communication_skill": "Comm. (1-5)" # --- NEW: Added new column ---
                },
                use_container_width=True
            )
            
            # --- NEW: UI/UX Change (Two columns for forms) ---
            col1, col2 = st.columns(2)
            
            with col1:
                # --- TPO DELETE FORM ---
                with st.container(border=True):
                    st.subheader("Delete a Student Record")
                    with st.form("delete_form"):
                        delete_id = st.number_input("Enter Student ID to DELETE", min_value=1, step=1)
                        delete_submitted = st.form_submit_button("Delete Record")
                    
                    if delete_submitted:
                        if delete_student_from_db(delete_id):
                            st.success(f"Successfully deleted student record with ID: {delete_id}")
                            st.experimental_rerun()
                        else:
                            st.error("Could not delete record. Check the ID.")
            
            with col2:
                # --- TPO JOB POSTING FORM ---
                with st.container(border=True):
                    st.subheader("📢 Post a New Job Opening")
                    with st.form("new_job_form"):
                        job_title = st.text_input("Job Title")
                        job_company = st.text_input("Company Name")
                        job_desc = st.text_area("Job Description & Requirements")
                        job_submitted = st.form_submit_button("Post Job")
                    
                    if job_submitted:
                        if not job_title or not job_desc:
                            st.warning("Please fill out all job fields.")
                        else:
                            if post_new_job(job_title, job_company, job_desc):
                                st.success(f"Successfully posted job: {job_title}")
                                st.experimental_rerun()
                            else:
                                st.error("Error posting job.")
                        
        except Exception as e:
            st.error(f"Error reading from database: {e}")
            
    elif password:
        st.error("Incorrect Password. Access Denied.")