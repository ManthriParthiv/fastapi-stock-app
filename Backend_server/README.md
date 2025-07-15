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


C:\Users\bdeer\OneDrive\Desktop\fastapi-stock-app\
└── Backend_server\
    ├── main.py                        # 🔹 FastAPI app
    ├── tickers.py                     # 🔹 CSV loader module
    └── tickers_with_names.csv         # 📄 CSV file with ticker data


