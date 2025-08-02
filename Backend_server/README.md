FastAPI Stock App

Project Setup Steps

1. Create a virtual environment:
   python -m venv myenv

2. Activate the virtual environment:
   On Windows:
       myenv\Scripts\activate

3. Download the requirements on project directory :
   pip install -r requirements.txt

3. Change to the project directory :
   cd quantum_optimiser
   Then install the required packages;
   pip install -r requirements.txt

4. Run the FastAPI development server:
   Come back to Backend server directory and run the server;
   python main.py

- Base URL: http://127.0.0.1:8000

Folder Structure


C:\Users\bdeer\OneDrive\Desktop\fastapi-stock-app\
└── Backend_server\
    ├── main.py                        # 🔹 FastAPI app
    ├── tickers.py                     # 🔹 CSV loader module
    └── tickers_with_names.csv         # 📄 CSV file with ticker data
    └── requirements.txt               # 🔹 pip requirements file
    └── quantum_optimizer           
         └── data
         └── postprocessing
         └── preprocessing
         └── requirements.txt
└── frontend_UI
      └── Stocks_App
         └── src
            └── components
            └── styles
         └── public
         └── .gitignore