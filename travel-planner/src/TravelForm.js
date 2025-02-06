import React, { useState } from 'react';
import { FaPlane, FaCar, FaHotel, FaSearch, FaLeaf, FaSun, FaMoon } from 'react-icons/fa'; // Import icons
import './App.css'; // Import the CSS file

const TravelForm = () => {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [result, setResult] = useState('');
  const [darkMode, setDarkMode] = useState(false); // Default to light mode
  const [itinerary, setItinerary] = useState(null); // Store parsed itinerary

  const handleSubmit = (e) => {
    e.preventDefault();
    setResult(`Traveling from ${source} to ${destination}`);

    // Simulate fetching itinerary data (replace with actual API call)
    const sampleItinerary = {
      flights: [
        { from: 'CLT', to: 'RDU', emissions: 20.76 },
        { from: 'IAD', to: 'RDU', emissions: 35.91 },
        { from: 'DCA', to: 'RDU', emissions: 36.34 },
        { from: 'PHL', to: 'RDU', emissions: 53.98 },
        { from: 'LGA', to: 'RDU', emissions: 68.98 },
      ],
      hotels: [
        { name: 'Ramada Raleigh', emissions: 5.94 },
        { name: 'Red Roof Inn 1090 Raleigh', emissions: 5.94 },
        { name: 'La Quinta Raleigh NC', emissions: 5.94 },
        { name: 'Hyatt Place Raleigh', emissions: 10.11 },
        { name: 'Four Points Raleigh Arena', emissions: 10.11 },
      ],
    };

    setItinerary(sampleItinerary);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
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
            <button type="submit" className="submit-button">
              Plan Trip
            </button>
          </form>

          {/* Result */}
          {result && <p className="result">{result}</p>}

          {/* Itinerary Cards */}
          {itinerary && (
            <div className="itinerary-cards">
              {/* Flight Cards */}
              <h3>Flight Options</h3>
              <div className="cards-container">
                {itinerary.flights.map((flight, index) => (
                  <div key={index} className="card">
                    <h4>
                      {flight.from} → {flight.to}
                    </h4>
                    <p>Carbon Emissions: {flight.emissions} kg CO₂</p>
                  </div>
                ))}
              </div>

              {/* Hotel Cards */}
              <h3>Hotel Options</h3>
              <div className="cards-container">
                {itinerary.hotels.map((hotel, index) => (
                  <div key={index} className="card">
                    <h4>{hotel.name}</h4>
                    <p>Carbon Emissions: {hotel.emissions} kg CO₂</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default TravelForm;