📈 Stock Tracker App




### 🖥 Frontend
- React + Bootstrap
- React Router
- Axios
- Responsive UI with tracked-stock drawer

## 🌐 Features

### ✅ Stock List Page
- Paginated tickers from a CSV file
- Real-time stock data fetched via `yfinance`
- Tracked stocks stored in `localStorage`
- Mobile-responsive layout

### ✅ Drawer & Search
- Add/remove stocks to a drawer (local tracking)
- Search stock by name or ticker symbol

### ✅ Analysis Page
- "Analyse" button sends selected tickers to backend
- Returns mock ML scores for recommendation

---

## 🗂️ Project Structure

📁 root/
├── backend/
│ ├── main.py # FastAPI app
│ ├── tickers.py # CSV loader function
│ └── tickers.csv # Stock symbol + name list
│
├── frontend/
│ ├── src/
│ │ ├── App.js # Stock list + tracker component
│ │ ├── LandingPage.js # Landing screen
│ │ ├── ResultsPage.js # ML result view
│ │ └── styles/ # Custom CSS (Stocks.css, Home.css, etc.)
│ └── public/
│ └── bg.jpg # Background image for landing
│
├── README.md
└── package.json / requirements.txt