import React, { useState } from 'react';
import { FaPlane, FaCar, FaHotel, FaSearch, FaLeaf, FaSun, FaMoon, FaMapMarkerAlt, FaBed, FaTimes } from 'react-icons/fa'; // Import icons
import './App.css'; // Import the CSS file

const TravelForm = () => {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [result, setResult] = useState('');
  const [darkMode, setDarkMode] = useState(false); // Default to light mode
  const [itinerary, setItinerary] = useState(null); // Store parsed itinerary
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [selectedCard, setSelectedCard] = useState(null); // Selected card for detailed view

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(`Traveling from ${source} to ${destination}`);

    try {
      // Call the Django API
      const apiUrl = import.meta.env.VITE_APP_API_URL;
      console.log(apiUrl);
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source: source,
          destination: destination,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch itinerary data');
      }

      const data = await response.json(); // Parse the outer JSON

      // Parse the nested JSON string in the "answer" field
      const outerParsed = JSON.parse(data.response.answer);

      // Set the itinerary data from the API response
      setItinerary(outerParsed);
    } catch (err) {
      setError(err.message); // Handle errors
    } finally {
      setLoading(false); // Stop loading
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleCardClick = (cardData, type) => {
    setSelectedCard({ ...cardData, type }); // Set the selected card for detailed view
  };

  const closeDetailedCard = () => {
    setSelectedCard(null); // Close the detailed card view
  };

  return (
    <div className={`app-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      {/* Header */}
      <header className="header">
        <div className="logo">
          <FaLeaf className="logo-icon" />
          <span>Sustainable Travel Planner</span>
        </div>
        <button onClick={toggleDarkMode} className="mode-toggle">
          {darkMode ? <FaSun /> : <FaMoon />} {/* Sun icon for light mode, moon for dark mode */}
        </button>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Plan Your Eco-Friendly Journey</h1>
          <p>Travel sustainably and reduce your carbon footprint with our planner.</p>
        </div>
      </section>

      {/* Travel Form Section */}
      <section className="travel-form-section">
        <div className="travel-form-container">
          <h2>Sustainable Travel Planner</h2>
          <p className="subtitle">Enter your details to plan your trip</p>

          {/* Icons Section */}
          <div className="icons-section">
            <div className="icon-item">
              <FaPlane className="icon" />
              <span>Flights</span>
            </div>
            <div className="icon-item">
              <FaCar className="icon" />
              <span>Cars</span>
            </div>
            <div className="icon-item">
              <FaHotel className="icon" />
              <span>Hotels</span>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label htmlFor="source">
                <FaSearch className="input-icon" /> Source:
              </label>
              <input
                type="text"
                id="source"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                placeholder="Enter source"
                required
              />
            </div>
            <div className="input-group">
              <label htmlFor="destination">
                <FaSearch className="input-icon" /> Destination:
              </label>
              <input
                type="text"
                id="destination"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Enter destination"
                required
              />
            </div>
            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Planning...' : 'Plan Trip'}
            </button>
          </form>

          {/* Result */}
          {result && <p className="result">{result}</p>}

          {/* Error Message */}
          {error && <p className="error-message">{error}</p>}

          {/* Loading Screen */}
          {loading && (
            <div className="loading-screen">
              <div className="loading-spinner"></div>
              <p>Planning your trip...</p>
            </div>
          )}

          {/* Itinerary Cards */}
          {itinerary && (
            <div className="itinerary-cards">
              {/* Flight Cards */}
              <h3>Flight Options</h3>
              <div className="cards-container">
                {itinerary.flight_options.map((flight, index) => (
                  <div
                    key={index}
                    className="card flight-card"
                    onClick={() => handleCardClick(flight, 'flight')}
                  >
                    <div className="card-icon">
                      <FaPlane />
                    </div>
                    <h4>
                      {flight.source} → {flight.destination}
                    </h4>
                    <p>
                      <strong>Carbon Emissions:</strong> {flight.carbon_emission} kg CO₂
                    </p>
                    <p>
                      <strong>Miles:</strong> {flight.miles}
                    </p>
                  </div>
                ))}
              </div>

              {/* Hotel Cards */}
              <h3>Hotel Options</h3>
              <div className="cards-container">
                {itinerary.hotel_options.map((hotel, index) => (
                  <div
                    key={index}
                    className="card hotel-card"
                    onClick={() => handleCardClick(hotel, 'hotel')}
                  >
                    <div className="card-icon">
                      <FaBed />
                    </div>
                    <h4>{hotel.hotel_name}</h4>
                    <p>
                      <FaMapMarkerAlt /> {hotel.location}
                    </p>
                    <p>
                      <strong>Type:</strong> {hotel.hotel_type}
                    </p>
                    <p>
                      <strong>Carbon Emissions:</strong> {hotel.carbon_emission} kg CO₂
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Detailed Card View */}
      {selectedCard && (
        <div className="detailed-card-overlay">
          <div className={`detailed-card ${darkMode ? 'dark-mode' : ''}`}>
            <button className="close-button" onClick={closeDetailedCard}>
              <FaTimes />
            </button>
            {selectedCard.type === 'flight' ? (
              <>
                <div className="card-icon">
                  <FaPlane />
                </div>
                <h4>
                  {selectedCard.source} → {selectedCard.destination}
                </h4>
                <p>
                  <strong>Carbon Emissions:</strong> {selectedCard.carbon_emission} kg CO₂
                </p>
                <p>
                  <strong>Miles:</strong> {selectedCard.miles}
                </p>
              </>
            ) : (
              <>
                <div className="card-icon">
                  <FaBed />
                </div>
                <h4>{selectedCard.hotel_name}</h4>
                <p>
                  <FaMapMarkerAlt /> {selectedCard.location}
                </p>
                <p>
                  <strong>Type:</strong> {selectedCard.hotel_type}
                </p>
                <p>
                  <strong>Carbon Emissions:</strong> {selectedCard.carbon_emission} kg CO₂
                </p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TravelForm;