import React, { useEffect, useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '../styles/Stocks.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const current_Stocks = ["IDEA.NS", "NHPC.NS", "SIEMENS.NS", "TCS.NS"];
export default function App() {
  const [page, setPage] = useState(1);
  const [stockList, setStockList] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockDetails, setStockDetails] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [searchFeedback, setSearchFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedStocksOption,setSelectedStocksOption]=useState('All Stocks');
  const [trackedStocks, setTrackedStocks] = useState([]);
  const [showDrawer, setShowDrawer] = useState(false);
  const [screenWidth, setScreenWidth] = useState(window.innerWidth);
  const [selectedAnalysisOption, setSelectedAnalysisOption] = useState('VQE-Optimisation');
const AvailableStocks=["All Stocks","Avaiable stocks"]
  useEffect(() => {
    setTrackedStocks(prev => {
      return JSON.parse(window.localStorage.getItem('trackedStocks')) || [];
    });
  }, []);

  const navigate = useNavigate();

  useEffect(() => {
    const handleResize = () => setScreenWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMdOrSm = screenWidth < 950

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/stocks?page=${page}&limit=50`);
        const data = res.data;
        setStockList(prev => {
          const merged = [...prev, ...data];
          const unique = new Set();
          return merged.filter(stock => {
            if (unique.has(stock.ticker)) return false;
            unique.add(stock.ticker);
            return true;
          });
        });
      } catch (err) {
        alert('❌ Failed to load stock list:', err);
      }
    };
    fetchStocks();
  }, [page]);

  const handleSelect = async (ticker) => {
    setLoading(true);
    setSearchFeedback('');
    try {
      setSelectedStock(ticker);
      const res = await axios.get(`http://localhost:8000/stock/${ticker}`);
      setStockDetails(res.data);      
    } catch (err) {
      alert('❌ Failed to fetch stock details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    const input = searchText.trim().toLowerCase();
    if (!input) return;
    const exact = stockList.find(item => item.ticker.toLowerCase() === input);
    if (exact) {
      handleSelect(exact.ticker);
      setSearchText('');
      return;
    }
    handleSelect(searchText.trim().toUpperCase());
    setSearchText('');
  };

  const toggleStockTracking = (ticker) => {
    
    setTrackedStocks(prev =>
      prev.includes(ticker) ? prev.filter(item => item !== ticker) : [...prev, ticker]
    );
  };

  const navigateTo = () => {
    window.localStorage.setItem('trackedStocks', JSON.stringify([...trackedStocks]));
    navigate('/analysed-stocks', {
      state: {
        trackedStocks: trackedStocks,
        analysisOption: selectedAnalysisOption // Pass the selected analysis option
      }
    });
  };

  return (
    <div className="app-container">
      {/* 🔷 Navbar */}
      <nav className="navbar navbar-dark bg-dark px-3 d-flex justify-content-between align-items-center">
        <span className="navbar-brand d-flex align-items-center pl-3 pr-3 mr-5">
          <i className="bi bi-bar-chart-fill me-2"></i>Stock Tracker
        </span>

        <div className="d-flex align-items-center gap-4">
          {/* 🛒 Cart Icon with Badge */}
          <div className="position-relative" onClick={() => setShowDrawer(true)} style={{ cursor: 'pointer' }}>
            <i className="bi bi-cart-fill text-white fs-4"></i>
            <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
              {trackedStocks.length}
            </span>
          </div>

          {/* New Dropdown for Analysis Options */}
          <select
            className="form-select form-select-sm bg-secondary text-white"
            style={{ width: 'auto', minWidth: '150px' }}
            onChange={(e) => setSelectedAnalysisOption(e.target.value)}
          >
            <option value="VQE-Optimisation">VQE-Optimisation</option>
          </select>

          <button className="btn btn-primary analyse-btn" onClick={() => { navigateTo() }}>Analyse</button>
        </div>
      </nav>

      {/* 🧾 Drawer for Tracked Stocks */}
      <div className={`stock-drawer ${showDrawer ? 'open' : ''}`}>
        <div className="drawer-header d-flex justify-content-between align-items-center px-3 py-2 bg-dark text-white">
          <h5 className="mb-0">Tracked Stocks</h5>
          <button className="btn btn-sm btn-outline-light" onClick={() => setShowDrawer(false)}>Close</button>
        </div>
        <div className="drawer-body p-3 overflow-auto">
          {trackedStocks.length === 0 ? (
            <p className="text-muted">No stocks added yet.</p>
          ) : (
            trackedStocks.map((ticker, index) => {
              const stock = stockList.find(s => s.ticker === ticker);
              return (
                <div key={index} className="tracked-item border-bottom py-2">
                  <strong>{ticker}</strong> - <span className="text-muted">{stock?.name || ''}</span>
                  <button
                    className="btn btn-sm btn-link text-danger float-end"
                    onClick={() => toggleStockTracking(ticker)}
                  >
                    Remove
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* 📄 Main Content */}
      <div className="d-flex main-content">
        <aside
          className="stock-list"
          style={{ width: isMdOrSm ? '30%' : '350px', minWidth: '150px' }}
        >
                      <select   onChange={(e)=>{
                       setSelectedStocksOption(e.target.value)}} className="form-select form-select-sm fw-bolder bg-secondary mb-3 ps-3 p-2 bold bg-Peach text-white">
                      {AvailableStocks.map((e)=>
                        (<option value={e}>{e}</option>)
                      )}
                      </select>

          <div className="input-group mb-3">
            <input
              type="text"
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              className="form-control"
              placeholder="Search ticker or name"
            />
            <button className="btn btn-outline-secondary" onClick={handleSearch}>
              <i className="bi bi-search"></i>
            </button>
          </div>

          {stockList.map(stock =>(selectedStocksOption=="All Stocks")?(
            <div
              key={stock.ticker}
              className={`stock-item ${selectedStock === stock.ticker ? 'active' : ''}`}
              onClick={() => handleSelect(stock.ticker)}
            >
              <h6 className="mb-0">{stock.ticker}</h6>
              {!isMdOrSm && <p className="mb-1 small"> {stock.name}</p>}
            </div>
          ):current_Stocks.indexOf(stock.ticker)!=-1 && ( <div
              key={stock.ticker}
              className={`stock-item ${selectedStock === stock.ticker ? 'active' : ''}`}
              onClick={() => handleSelect(stock.ticker)}
            >
              <h6 className="mb-0">{stock.ticker}</h6>
              {!isMdOrSm && <p className="mb-1  small">{stock.name}</p>}
            </div>))}

          <button className="btn btn-primary w-100 mt-5 bg-transparent" onClick={() => setPage(prev => prev + 1)}>
            Load More
          </button>
        </aside>
        <div className="stock-details flex-fill p-3 mt-2">
          {!selectedStock && (
            <div className="placeholder">
              <i className="bi bi-info-circle me-2" style={{ fontSize: '2rem' }}></i>
              Select a stock to view details
            </div>
          )}

          {searchFeedback && (
            <div className="alert alert-info small p-2 mb-2">{searchFeedback}</div>
          )}

          {loading && (
            <div className="text-center my-5">
              <div className="spinner-border text-primary" role="status"></div>
              <p className="mt-2">Loading details...</p>
            </div>
          )}

          {stockDetails && !loading && (
            <div className="details-card card shadow-sm mt-2">
              <div className="card-header bg-primary text-white d-flex align-items-center">
                <i className="bi bi-graph-up me-2"></i>
                <h5 className="mb-0"> {stockDetails.Ticker}</h5>
              </div>
              <div className="card-body">
                <table className="table table-sm mb-0">
                  <tbody>
                    <tr>
                      <th>Volume</th>
                      <td>{stockDetails.Volume ? Number(stockDetails.Volume).toLocaleString() : ''}</td>
                    </tr>
                    <tr>
                      <th>P/E Ratio</th>
                      <td>{stockDetails.PE}</td>
                    </tr>
                    <tr>
                      <th>P/B Ratio</th>
                      <td>{stockDetails.PB}</td>
                    </tr>
                    <tr>
                      <th>ROE</th>
                      <td>{stockDetails.ROE}</td>
                    </tr>
                    <tr>
                      <th>Earnings Date</th>
                      <td>{stockDetails.EarningsDate}</td>
                    </tr>
                  </tbody>
                </table>

                <button
                  className="btn btn-sm btn-outline-primary m-3"
                  onClick={() =>{ (current_Stocks.indexOf(selectedStock) != -1) ? toggleStockTracking(stockDetails.Ticker) : ''}}
                  style={
                    trackedStocks.includes(stockDetails.Ticker)
                      ? { backgroundColor: 'red', color: 'black' }
                      : {}
                  }
                >
                  {(current_Stocks.indexOf(selectedStock) !== -1) ? (trackedStocks.includes(stockDetails.Ticker)
                    ? 'Remove from analysis'
                    : 'Add for analysis' ): 'Not available for analysis'}

                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}