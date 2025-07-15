import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/Home.css';
import axios from 'axios';

export default function LandingPage() {
  const [imageLoaded, setImageLoaded] = useState(false);
 const navigate = useNavigate();
  useEffect(() => {
    const img = new Image();
img.src = '/bg.jpg';
    img.onload = () => {
      setImageLoaded(true); // Only then render the component
    };
  }, []);

  if (!imageLoaded) {
    return (
      <div className="loading-screen d-flex justify-content-center align-items-center vh-100 vw-100 bg-dark text-white">
        <h2>Loading...</h2>
      </div>
    );
  }
  return (
    <div className="landing-container text-white text-center">
      <div className="overlay"></div>

      <div className="content">
        <h1 className="display-3 fw-bold mb-4">📊 Welcome to Stock Tracker</h1>
        <p className="lead mb-5">
          Real-time insights, detailed analysis,<br /> all in one sleek dashboard.
        </p>
        <button className="btn btn-lg btn-primary px-4 " onClick={()=>navigate('/Stocks')}>
          Go to Stock Tracker 🚀
        </button>
      </div>

      <footer className="footer text-center mt-auto text-white-50">
        <p className="mb-0">© {new Date().getFullYear()} Anantwave Company</p>
      </footer>
    </div>
  );
}
