# AcroConnect: The AITR Placement Readiness Platform 🎓

An AI-powered full-stack web application designed to revolutionize the Training & Placement Office (TPO) process and empower students with personalized career roadmaps.

## Project Overview

AcroConnect addresses the critical disconnect between student skills, industry demands, and the manual processes often used by college TPOs. By leveraging Artificial Intelligence (specifically Google Gemini), it aims to provide:

1.  **Personalized Career Roadmaps:** AI-driven guidance for students based on their profile, skills, and career goals.
2.  **TPO Analytics Dashboard:** Real-time, data-driven insights for the TPO to efficiently manage student data and job placements.
3.  **Centralized Data Management:** A robust database for student profiles, job postings, and skill requirements.

## Key Features (Proof of Concept)

* Student Profile Creation & Management
* AI-Generated Career Roadmap Recommendations
* TPO Dashboard for Student Data Overview
* Secure Login/Authentication (for TPO)
* Database Integration (SQLite for PoC, PostgreSQL for full project)

## Technology Stack

* **Frontend:** Streamlit (Python-based web framework)
* **Backend:** Flask API (Python, for full project)
* **Database:** SQLite (for PoC), PostgreSQL (for full project)
* **AI/ML:** Google Gemini API
* **Version Control:** Git, GitHub

## Setup and Installation (PoC)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Varun2344/AcroConnect-
    cd AcroConnect
    ```
2.  **Create a Python Virtual Environment:**
    ```bash
    python -m venv .venv
    ```
3.  **Activate the Virtual Environment:**
    * **Windows:** `.\.venv\Scripts\activate`
    * **macOS/Linux:** `source ./.venv/bin/activate`
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create a `.env` file:**
    Create a file named `.env` in the root of the project and add your Google Gemini API key:
    ```
    GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
    ```
6.  **Run the Streamlit Application:**
    ```bash
    streamlit run app.py
    ```

## Development Team

* Varun Purohit (0827CI221148) - [Your Role]
* Varun Bhaisare (0827CI221147) - [Their Role]
* Mohd. Ayan Mansuri (0827CI221093) - [Their Role]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.