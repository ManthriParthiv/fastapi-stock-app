FastAPI Stock App

Project Setup Steps

1. Create a virtual environment:
   python -m venv myenv

2. Activate the virtual environment:
   On Windows:
       myenv\Scripts\activate

3. Install the required packages:
   pip install -r requirements.txt

4. Run the FastAPI development server:
   uvicorn app.main:app --reload

- Base URL: http://127.0.0.1:8000

Folder Structure


app/
├── main.py     # Starts the FastAPI app
├── routes/     # API endpoints (like /optimize)
├── models/     # Data models using Pydantic
└── services/   # Logic for portfolio optimization

requirements.txt         # List of Python dependencies
README.txt               # You are reading this!
.gitignore               # Files and folders to ignore in Git

Notes
- Make sure to activate your virtual environment every time before running the server.



