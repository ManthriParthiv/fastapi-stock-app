import React, { useEffect, useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '../styles/AnalysedStock.css';
import axios from 'axios';
import {data, useLocation} from 'react-router-dom';

export default function ResultsPage() {
  const [bestStocks, setBestStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const location=useLocation()
  const Data={'tickers':location.state.trackedStocks || []}
  useEffect(() => {
    const fetchBestStocks = async () => {
      try {
        const res = await axios.post('http://localhost:8000/stocks/ml-results',Data);
        const data = res.data;        
        setBestStocks(data);
      } catch (err) {
        alert('❌ Failed to load analysis results');
      } finally {
        setLoading(false);
      }
    };

    fetchBestStocks();
  }, []);

  return (
    <div className="result-wrapper d-flex flex-column justify-content-center align-items-center vh-100 px-3">
      <h2 className="text-center mb-4">
        <i className="bi bi-bar-chart-line-fill me-2 text-primary"></i>
        ML-Based Stock Recommendations
      </h2>

      {loading ? (
        <div className="text-center mt-4">
          <div className="spinner-border text-primary" role="status"></div>
          <p className="mt-3">Fetching insights...</p>
        </div>
      ) : bestStocks.length === 0 ? (
        <p className="text-center text-muted">No recommendations available.</p>
      ) : (
        <div className="results-list w-100 d-flex flex-column align-items-center">
          {bestStocks.map((stock, index) => (
            <div key={index} className="result-card card shadow-sm mb-4 p-3">
              <div className="d-flex align-items-center gap-3">
                <div className="icon-wrap">
                  <i className="bi bi-graph-up-arrow fs-2 text-success"></i>
                </div>
                <div className="stock-info text-start">
                  <h5 className="mb-1 fw-semibold">{stock.ticker}</h5>
                  <p className="mb-1 text-muted small">{stock.name}</p>
                  {stock.score && (
                    <span className="badge bg-light text-dark">
                      Confidence: {(stock.score * 100).toFixed(2)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
