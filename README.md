# Project 19 – Advanced Course Registration System

This project is a full-stack application with a React frontend and a Flask backend to demonstrate an advanced course registration system using an Oracle database.

## Prerequisites

- Python 3.x
- Node.js and npm
- Oracle Database 21c

## Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure the database connection:**
    -   Open `backend/db_config.py` and fill in your Oracle database credentials:
        ```python
        DB_USER = "your_username"
        DB_PASSWORD = "your_password"
        DB_DSN = "your_dsn"
        ```

6.  **Run the Flask server:**
    ```bash
    flask run --port 5001
    ```

## Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the dependencies:**
    ```bash
    npm install
    ```

3.  **Run the Vite development server:**
    ```bash
    npm run dev
    ```

4.  **Open your browser and navigate to `http://localhost:5173` (or the address shown in your terminal).**

## How to Use

1.  **Login:** Use the credentials for the different roles (admin, teacher, student) that you have created in your database.
2.  **Dashboards:** Based on your role, you will be redirected to the appropriate dashboard.
    -   **Student:** View courses, sections, and register for a section, view grades.
    -   **Teacher:** View assigned sections and submit grades, view students.
    -   **Admin:** View section capacity, registration details, teachers, courses, sections, students. Also includes forms for adding/updating/deleting courses, sections, teachers, and students.