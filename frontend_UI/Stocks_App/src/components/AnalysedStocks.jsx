import React, { useEffect, useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '../styles/AnalysedStock.css'; 
import axios from 'axios';
import { useLocation } from 'react-router-dom';

export default function ResultsPage() {
  // bestStocks will now hold the entire response object (tickers, weights, risk)
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  const requestData = {
    tickers: location.state?.trackedStocks || [], // Use optional chaining for safety
    analysisOption: location.state.analysisOption  // Pass the selected option
  };
  useEffect(() => {
    const fetchAnalysisResults = async () => {
      if (requestData.tickers.length === 0) {
        setLoading(false);
        setAnalysisResults(null); 
        return;
      }

      try {
        const res = await axios.post('http://127.0.0.1:8000/quantum/optimize', requestData);
        const data = res.data;
        setAnalysisResults(data); // Store the entire response
      } catch (err) {
        console.error('❌ Failed to load analysis results:', err);
        alert('❌ Failed to load analysis results. Please try again.');
        setAnalysisResults(null); // Clear results on error
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisResults();
  }, [requestData.tickers, requestData.analysisOption]); // Re-run effect if trackedStocks or analysisOption changes

  return (
    <div className="result-wrapper d-flex flex-column justify-content-center align-items-center vh-100 px-3">
      <h2 className="text-center mb-4">
        <i className="bi bi-pie-chart-fill me-2 text-primary"></i>
        {requestData.analysisOption}
      </h2>

      {loading ? (
        <div className="text-center mt-4">
          <div className="spinner-border text-primary" role="status"></div>
          <p className="mt-3">Optimizing your portfolio...</p>
        </div>
      ) : (analysisResults && analysisResults.tickers && analysisResults.tickers.length > 0) ? (
        <div className="results-container w-100 d-flex flex-column align-items-center">
          <div className="card shadow-sm mb-4 p-4 w-75"> {/* Increased width */}
            <h4 className="card-title text-center mb-3">Recommended {requestData.analysisOption}</h4>
            <div className="table-responsive">
              <table className="table table-striped table-hover mb-3">
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Recommended Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.tickers.map((ticker, index) => (
                    <tr key={index}>
                      <td><strong>{ticker}</strong></td>
                      <td>{(analysisResults.weights[ticker])}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="alert alert-info text-center mt-3">
              <strong>Overall Risk:</strong> {(analysisResults.risk)}%
            </div>
          </div>
        </div>
      ) : (
        <p className="text-center text-muted">
          No portfolio optimization results available. Please track some stocks first.
        </p>
      )}
    </div>
  );
}