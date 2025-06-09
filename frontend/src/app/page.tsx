"use client"
import React, { useState, FormEvent, useEffect } from 'react';
import Head from 'next/head'; // Import Head for managing document head

const App: React.FC = () => {
  const [url, setUrl] = useState<string>('');
  const [clonedHtml, setClonedHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>('checking...');

  // Effect to check backend health on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          const data = await response.json();
          setBackendStatus(data.status);
        } else {
          setBackendStatus('unhealthy');
        }
      } catch (err) {
        setBackendStatus('unreachable');
      }
    };
    checkBackendHealth();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setClonedHtml(null); // Clear previous content

    try {
      // Assuming your FastAPI backend is running on http://localhost:8000
      const response = await fetch('http://localhost:8000/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to clone website');
      }

      const data = await response.json();
      setClonedHtml(data.cloned_html);
      console.log('Cloned HTML:', data.cloned_html);
    } catch (err: any) {
      console.error('Cloning error:', err);
      setError(err.message || 'An unexpected error occurred during cloning.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Orchids Website Cloner</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
        {/* Using a font more similar to the screenshot for headings */}
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap" rel="stylesheet" />
      </Head>

      {/* Global and component-specific styles */}
      <style jsx global>{`
        /* Global Reset & Base Styles */
        body {
          font-family: 'Inter', sans-serif;
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
          min-height: 100vh;
          background-color: #1a1a1a; /* Dark background from screenshot */
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: flex-start; /* Align content to top */
          padding: 0; /* Remove body padding */
          color: #e0e0e0; /* Light text for dark background */
        }

        .header {
          width: 100%;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 2rem;
          background-color: #1a1a1a;
          color: #e0e0e0;
          position: fixed;
          top: 0;
          z-index: 10;
        }

        .header .logo {
          font-family: 'Inter', sans-serif;
          font-weight: 600;
          font-size: 1.2rem;
          color: #fff;
        }

        .header .nav-links {
          display: flex;
          gap: 1.5rem;
          align-items: center;
        }

        .header .nav-link {
          color: #e0e0e0;
          text-decoration: none;
          font-size: 0.9rem;
          font-weight: 500;
          transition: color 0.2s ease-in-out;
        }

        .header .nav-link:hover {
          color: #fff;
        }

        .header .login-signup-btn {
          background-color: #fff;
          color: #1a1a1a;
          padding: 0.5rem 1rem;
          border-radius: 9999px; /* Pill shape */
          font-weight: 600;
          font-size: 0.9rem;
          border: none;
          cursor: pointer;
          transition: background-color 0.2s ease-in-out;
        }

        .header .login-signup-btn:hover {
          background-color: #f0f0f0;
        }

        /* Main content container (was main-card) */
        .main-container {
          max-width: 60rem; /* Adjusted for wider layout */
          width: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 8rem 2rem 3rem 2rem; /* Adjusted top padding for fixed header */
          text-align: center;
          min-height: calc(100vh - 4rem); /* Adjust for header height */
          justify-content: center; /* Center content vertically if space allows */
        }
        
        .clover-icon {
          width: 60px; /* Adjust size as needed */
          height: 60px;
          background-color: #ff69b4; /* Pink color from screenshot */
          border-radius: 50%; /* Circle */
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 3rem;
          color: #1a1a1a;
          font-weight: bold;
          margin-bottom: 2rem;
          /* Simple cross shape with pseudo-elements */
          position: relative;
        }
        .clover-icon::before, .clover-icon::after {
          content: '';
          position: absolute;
          background-color: #1a1a1a;
          border-radius: 50%;
        }
        .clover-icon::before {
          width: 20px;
          height: 20px;
          top: 10px; left: 10px;
        }
        .clover-icon::after {
          width: 20px;
          height: 20px;
          bottom: 10px; right: 10px;
        }
        /* More complex clover shape can be done with SVG or more pseudo-elements */


        .heading {
          font-family: 'Playfair Display', serif; /* Distinct font for heading */
          font-size: 3.5rem; /* Larger heading */
          font-weight: 700;
          color: #ffffff;
          line-height: 1.1;
          margin-bottom: 1rem;
        }

        .sub-heading {
          font-size: 1.2rem;
          color: #a0a0a0; /* Lighter grey for sub-heading */
          margin-bottom: 2rem;
        }

        .backend-status {
          font-size: 0.9rem;
          font-weight: 500;
          color: #a0a0a0;
          margin-bottom: 1.5rem;
        }

        .status-healthy {
          color: #34d399; /* green-500 */
        }

        .status-unhealthy {
          color: #f87171; /* red-400 */
        }

        .status-unreachable {
          color: #fbbf24; /* yellow-400 */
        }

        /* Form Styles */
        .form-container {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          width: 100%;
          max-width: 40rem; /* Match input field width */
        }

        .input-group {
          background-color: #333333; /* Darker background for input */
          border-radius: 0.75rem; /* rounded-xl */
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.06);
          overflow: hidden; /* Ensure border-radius applies */
          display: flex; /* Make input and button side-by-side if needed */
        }

        .url-input {
          flex-grow: 1;
          background-color: #333333; /* Darker background for input */
          border: none; /* No external border */
          padding: 1rem 1.25rem;
          color: #e0e0e0;
          font-size: 1rem;
          outline: none;
          transition: background-color 0.2s ease-in-out;
        }
        .url-input::placeholder {
          color: #888888;
        }
        .url-input:focus {
          background-color: #444444;
        }
        .url-input:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          background-color: #222222;
        }

        .submit-button {
          padding: 1rem 1.5rem;
          background-color: #555555; /* Dark grey for button */
          color: #ffffff;
          border: none;
          border-radius: 0.75rem; /* rounded-lg */
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background-color 0.2s ease-in-out, transform 0.2s ease-in-out;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
        }
        .submit-button:hover:not(:disabled) {
          background-color: #666666;
          transform: translateY(-2px); /* Slight lift on hover */
        }
        .submit-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          transform: none;
        }

        .loading-spinner {
          animation: spin 1s linear infinite;
          height: 1.25rem;
          width: 1.25rem;
          color: #ffffff;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .error-message {
          background-color: #4a1a1a; /* Dark red background */
          border: 1px solid #ff6969; /* Lighter red border */
          color: #ffcccc; /* Light red text */
          padding: 1rem;
          border-radius: 0.5rem;
          font-size: 0.9rem;
          text-align: left;
          margin-top: 1.5rem;
        }
        .error-message strong {
          font-weight: 700;
          margin-right: 0.5rem;
        }

        /* Cloned Website Preview Section */
        .preview-section {
          margin-top: 4rem; /* More space from input section */
          width: 100%;
          max-width: 80rem; /* Wider for preview */
          padding: 0 1rem; /* Padding for small screens */
        }
        .preview-title {
          font-size: 2rem;
          font-weight: 700;
          color: #ffffff;
          margin-bottom: 2rem;
          text-align: center;
        }

        /* Iframe container (from previous code) */
        .iframe-container {
          position: relative;
          width: 100%;
          padding-bottom: 75%; /* 4:3 Aspect Ratio for the iframe. Adjust as needed. */
          height: 0;
          overflow: hidden;
          background-color: #fff;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          border: 1px solid #222; /* Darker border */
        }
        .iframe-container iframe {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          border: none;
          transform-origin: top left;
          transform: scale(1);
        }
        @media (max-width: 640px) {
          .iframe-container {
            padding-bottom: 120%;
          }
        }

        /* Generated HTML (for inspection) section */
        .html-inspection-section {
          margin-top: 2rem;
          background-color: #111111; /* Even darker background for code */
          color: #e0e0e0;
          padding: 1.5rem;
          border-radius: 0.5rem;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          overflow: auto;
        }
        .html-inspection-section h3 {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 1rem;
          color: #ffffff;
        }
        .html-inspection-section pre {
          white-space: pre-wrap;
          word-break: break-all;
          font-size: 0.875rem;
          font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
          line-height: 1.625;
          background-color: #000000; /* Pure black for code block background */
          padding: 1rem;
          border-radius: 0.375rem;
          color: #b0b0b0; /* Lighter code text */
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
          .main-container {
            padding-top: 6rem;
            padding-left: 1rem;
            padding-right: 1rem;
          }
          .heading {
            font-size: 2.5rem;
          }
          .sub-heading {
            font-size: 1rem;
          }
        }

        @media (max-width: 480px) {
          .header {
            padding: 0.8rem 1rem;
          }
          .header .nav-links {
            gap: 1rem;
          }
          .header .login-signup-btn {
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
          }
          .heading {
            font-size: 2rem;
          }
          .sub-heading {
            font-size: 0.9rem;
          }
          .url-input, .submit-button {
            padding: 0.8rem 1rem;
            font-size: 0.9rem;
          }
          .preview-title {
            font-size: 1.5rem;
          }
          .html-inspection-section pre {
            font-size: 0.75rem;
          }
        }

        /* New/Updated Styles for Website Cards */
        .websites-made-section {
          width: 100%;
          max-width: 60rem;
          padding: 3rem 2rem;
          text-align: center;
        }

        .websites-made-title {
          font-family: 'Playfair Display', serif;
          font-size: 2.5rem;
          font-weight: 700;
          color: #ffffff;
          margin-bottom: 0.5rem;
        }

        .websites-made-subtitle {
          font-size: 1rem;
          color: #a0a0a0;
          margin-bottom: 2rem;
        }

        .category-buttons {
          display: flex;
          justify-content: center;
          flex-wrap: wrap; /* Allow wrapping on small screens */
          gap: 0.75rem;
          margin-bottom: 2rem;
        }

        .category-btn {
          background-color: #333333;
          color: #e0e0e0;
          padding: 0.6rem 1.2rem;
          border-radius: 9999px; /* Pill shape */
          border: 1px solid #555555;
          font-weight: 500;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
        }

        .category-btn.selected {
          background-color: #ffffff;
          color: #1a1a1a;
          border-color: #ffffff;
        }

        .category-btn:hover:not(.selected) {
          background-color: #444444;
          border-color: #777777;
        }

        .website-previews-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Responsive grid */
          gap: 1.5rem;
          justify-content: center; /* Center items in the grid */
          max-width: 100%; /* Ensure it doesn't overflow on wide screens */
          margin: 0 auto; /* Center the grid itself */
        }

        .website-card {
          background-color: #333333; /* Card background */
          border-radius: 0.75rem; /* Rounded corners */
          overflow: hidden; /* Hide image overflow */
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.06);
          transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center; /* Center content horizontally */
          padding-bottom: 1rem; /* Padding at bottom of card */
          text-align: center; /* Center text inside the card */
        }

        .website-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15), 0 3px 6px rgba(0, 0, 0, 0.09);
        }

        .website-card-img {
          width: 100%;
          height: auto; /* Maintain aspect ratio */
          max-height: 180px; /* Limit image height to prevent distortion in card */
          display: block;
          object-fit: cover; /* Cover the area, cropping if necessary */
          border-bottom: 1px solid #444444; /* Separator for image */
          margin-bottom: 0.75rem; /* Space below image */
        }
        
        .website-card p { /* Text below image */
            font-size: 0.95rem;
            color: #e0e0e0;
            padding: 0 0.75rem; /* Padding for text */
            text-align: center;
            line-height: 1.3;
        }
        
        /* Adjusted margin for cloned preview section */
        .cloned-preview-section {
          margin-top: 4rem; /* More space from input section */
          width: 100%;
          max-width: 80rem; /* Wider for preview */
          padding: 0 1rem; /* Padding for small screens */
        }

        @media (max-width: 600px) {
          .website-previews-grid {
            grid-template-columns: 1fr; /* Single column on very small screens */
          }
        }
      `}</style>

      {/* Header section - mimicking the Orchids.app header */}
      <header className="header">
        <div className="logo">orchids</div>
        <nav className="nav-links">
          <a href="https://www.linkedin.com/in/mohammed-abbas-rizvi-532204230/" className="nav-link">LinkedIn</a>
          <a href="mailto:mohammedabbasr9@gmail.com" className="nav-link">Email me</a>
          <button className="login-signup-btn">Sign up</button>
        </nav>
      </header>

      {/* Main content container */}
      <div className="main-container">
        {/* Clover Icon */}
        <div className="clover-icon"></div>

        <h1 className="heading">
          Make a website in seconds
        </h1>
        <p className="sub-heading">
          Start, iterate, and launch your website all in one place
        </p>

        {/* Backend Status */}
        <div className="backend-status">
          Backend Status: {' '}
          <span className={
            backendStatus === 'healthy' ? 'status-healthy' :
              backendStatus === 'unhealthy' ? 'status-unhealthy' :
                'status-unreachable'
          }>
            {backendStatus}
          </span>
        </div>

        {/* URL Input Form */}
        <form className="form-container" onSubmit={handleSubmit}>
          <div className="input-group">
            <label htmlFor="website-url" className="sr-only">
              Website URL
            </label>
            <input
              id="website-url"
              name="url"
              type="url"
              autoComplete="off" // Prevent browser autofill
              required
              className="url-input"
              placeholder="Make me a la" /* Placeholder as per screenshot */
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading || backendStatus !== 'healthy'} // Disable if loading or backend is not healthy
            />
            {/* The "up arrow" icon for submit */}
            <button
              type="submit"
              className="submit-button"
              disabled={loading || backendStatus !== 'healthy'}
            >
              {loading ? (
                <svg className="loading-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="19" x2="12" y2="5"></line>
                  <polyline points="5 12 12 5 19 12"></polyline>
                </svg>
              )}
            </button>
          </div>
        </form>

        {/* Error message display */}
        {error && (
          <div className="error-message" role="alert">
            <strong>Error:</strong>
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Cloned Website Preview Section (moved lower) */}
      {clonedHtml && (
        <div className="cloned-preview-section">
          <h2 className="cloned-preview-title">Cloned Website Preview:</h2>
          <div className="iframe-container">
            <iframe
              srcDoc={clonedHtml}
              title="Cloned Website Preview"
              sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-modals"
              loading="lazy"
            ></iframe>
          </div>
          {/* Section to display the raw generated HTML for inspection */}
          <div className="html-inspection-section">
            <h3>Generated HTML (for inspection):</h3>
            <pre>
              {clonedHtml}
            </pre>
          </div>
        </div>
      )}

      {/* Websites Made with Orchids Section */}
      <section className="websites-made-section">
        <h2 className="websites-made-title">Websites made with Orchids</h2>
        <p className="websites-made-subtitle">Click on any one to visit the live site</p>
        <div className="category-buttons">
          <button className="category-btn selected">Landing Pages</button>
        </div>
        {/* Placeholder for actual website cards/previews */}
        <div className="website-previews-grid">
          {/* Example Placeholder Cards */}
          <div className="website-card">
            <img src="/ss.png" alt="Landing Page Preview" className="website-card-img" />
            <p>This website design is inspired by {" "}
              <a href='https://www.orchids.app/'>
                orchids.app
            </a> </p> {/* Added content */}
          </div>
        </div>
      </section>

    </>
  );
};

export default App;
