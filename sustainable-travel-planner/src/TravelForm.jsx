import React, { useState,useMemo } from 'react';
import { FaPlane, FaCar, FaHotel, FaSearch, FaLeaf, FaSun, FaMoon, FaMapMarkerAlt, FaBed, FaTimes,FaUpload,FaCheckCircle } from 'react-icons/fa'; // Import icons
import './App.css'; // Import the CSS file
import { Box, Button, CardContent, IconButton, Paper, Typography } from '@mui/material';
import { UploadFile as UploadFileIcon, Delete as DeleteIcon, InsertDriveFile as FileIcon } from '@mui/icons-material';
import { useTheme, ThemeProvider, createTheme } from "@mui/material/styles";


const TravelForm = () => {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [result, setResult] = useState('');
  const [darkMode, setDarkMode] = useState(false); // Default to light mode
  const [itinerary, setItinerary] = useState(null); // Store parsed itinerary
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState(null); // Error state
  const [selectedCard, setSelectedCard] = useState(null); // Selected card for detailed view
  const [uploadedFile, setUploadedFile] = useState(null);
  const [calculatedMiles, setCalculatedMiles] = useState(null);
  const [calculatedEmissions, setCalculatedEmissions] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('manual');

  // Create a dynamic theme that updates on toggle
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? "dark" : "light",
        },
      }),
    [darkMode] // Theme will update when darkMode changes
  );


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
        console.log(data);

        // Check if "response" and "answer" exist and are valid
        if (!data.response || !data.response.answer) {
            throw new Error('Invalid response format from API');
        }

        // Parse the nested JSON in the "answer" field
        const outerParsed = data.response.answer;

        console.log(outerParsed);

        // // Validate the expected structure
        // const itinerary = {
        //     type: outerParsed.type,
        //     source: outerParsed.source,
        //     destination: outerParsed.destination,
        //     layover: outerParsed.layover || 'None',
        //     airline: outerParsed.airline || [],
        //     confidence: outerParsed.confidence,
        //     miles: outerParsed.miles,
        //     source_of_route: outerParsed.source_of_route,
        //     carbon_emission: outerParsed.carbon_emission || '0.0',
        // };

        // Set the itinerary data from the API response
        setItinerary(outerParsed);
    } catch (err) {
      console.log(err)
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

  const handleFileUpload = (e) => {
    const file = e.target.files[0];

    if (!file) {
      setError("No file selected.");
      return;
    }

    // Validate file type (CSV or Excel)
    const validExtensions = [".csv", ".xlsx"];
    const fileExtension = file.name.slice(((file.name.lastIndexOf(".") - 1) >>> 0) + 2);
    
    if (!validExtensions.includes(`.${fileExtension.toLowerCase()}`)) {
      setError("Invalid file type. Please upload a CSV or Excel file.");
      return;
    }

    setUploadedFile(file);
    setError(null);
    console.log("File uploaded:", file.name);
  };

  const deleteFile = () => {
    setUploadedFile(null);
    setCalculatedMiles(null);
    setSuccessMessage(null);
    setError(null);
    console.log("File deleted.");
  };

  const sendDataToBackend = async () => {
    if (!uploadedFile) {
        alert("Please upload a CSV file before calculating.");
        return;
    }

    setLoading(true);
    setError(null);
    setCalculatedMiles(null);
    setCalculatedEmissions(null);
    setSuccessMessage(null);

    try {
        const formData = new FormData();
        formData.append("file", uploadedFile);
        const milesUrl = import.meta.env.VITE_APP_MILES_URL;
        const response = await fetch(milesUrl, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to process CSV file.");
        }

        const data = await response.json();
        console.log("Backend Response:", data);

        // Set total miles & total emissions directly from API response
        if (data.status === "success") {
            setCalculatedMiles(data.total_miles || 0);
            setCalculatedEmissions(data.total_emissions || 0);
            setSuccessMessage("Miles and emissions successfully calculated!");
        }
    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
};

  const handleTabChange = (tab) => {
    setActiveTab(tab);
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

          <div className="tabs">
            <button className={activeTab === 'manual' ? 'active' : ''} onClick={() => handleTabChange('manual')}>
              Manual Input
            </button>
            <button className={activeTab === 'upload' ? 'active' : ''} onClick={() => handleTabChange('upload')}>
              Upload File
            </button>
          </div>

          

          {activeTab === 'manual' ? (
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
          ) : (
            <>
              {!uploadedFile ? (
                <Box mt={2} display="flex" justifyContent="center">
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<UploadFileIcon />}
                    color="primary"
                  >
                    Upload CSV or Excel
                    <input type="file" hidden accept=".csv, .xlsx" onChange={handleFileUpload} />
                  </Button>
                </Box>
              ) : (
                <Paper
                  elevation={3}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: 2,
                    borderRadius: 3,
                    mt: 2,
                    backgroundColor: theme.palette.mode === "dark" 
                      ? theme.palette.grey[800] 
                      : theme.palette.background.paper,
                    color: theme.palette.mode === "dark" 
                      ? theme.palette.grey[100] 
                      : theme.palette.text.primary,
                    boxShadow: theme.palette.mode === "dark" 
                      ? "0 4px 10px rgba(255, 255, 255, 0.1)" 
                      : "0 4px 10px rgba(0, 0, 0, 0.1)",
                    borderLeft: `4px solid ${theme.palette.mode === "dark" ? "#3498db" : "#007bff"}`, // Accent border
                  }}
                >
                  <FileIcon 
                    sx={{ 
                      fontSize: 40, 
                      color: theme.palette.mode === "dark" ? "#3498db" : "primary.main" 
                    }} 
                  />
                  <CardContent>
                    <Typography 
                      variant="subtitle1" 
                      fontWeight="bold"
                      sx={{
                        color: theme.palette.mode === "dark" ? "#ffffff" : "inherit"
                      }}
                    >
                      {uploadedFile.name}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: theme.palette.mode === "dark" ? "grey.400" : "textSecondary" 
                      }}
                    >
                      Size: {(uploadedFile.size / 1024).toFixed(2)} KB
                    </Typography>
                  </CardContent>
                  <IconButton 
                    onClick={deleteFile} 
                    sx={{ 
                      color: theme.palette.mode === "dark" ? "#e74c3c" : "error.main",
                      "&:hover": { color: theme.palette.mode === "dark" ? "#c0392b" : "error.dark" }
                    }}
                  >
                    <DeleteIcon fontSize="large" />
                  </IconButton>
                </Paper>
              )}

              {uploadedFile && (
                <Box display="flex" justifyContent="center" mt={2}>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={sendDataToBackend}
                    disabled={loading}
                  >
                    {loading ? 'Calculating...' : 'Calculate Miles'}
                  </Button>
                </Box>
              )}

            </>
          )}

          {activeTab === "upload" && (successMessage || calculatedMiles !== null || calculatedEmissions !== null) && (
            <div className="status-container">
              {/* Total Miles Display */}
              {calculatedMiles !== null && (
                <div className="miles-card">
                  <div className="miles-header">
                    <FaPlane className="miles-icon" />
                    <h3>Total Flight Distance</h3>
                  </div>
                  <p className="miles-value">{calculatedMiles} miles</p>
                </div>
              )}

              {/* Total Emissions Display */}
              {calculatedEmissions !== null && (
                <div className="emissions-card">
                  <div className="emissions-header">
                    <FaLeaf className="emissions-icon" />
                    <h3>Total CO₂ Emissions</h3>
                  </div>
                  <p className="emissions-value">{calculatedEmissions} T CO₂</p>
                </div>
              )}
            </div>
          )}

          
          {/* Result */}
          {activeTab === 'manual' && result && <p className="result">{result}</p>}

          {/* Error Message */}
          {error && <p className="error-message">{error}</p>}

          {/* Loading Screen */}
          {loading && (
            <div className="loading-screen">
              <div className="loading-box">
                <div className="loading-spinner"></div>
                <p className="loading-text">
                  {activeTab === "manual" ? "Planning your trip..." : "Calculating miles..."}
                </p>
              </div>
            </div>
          )}

          {/* Itinerary Cards */}
          {activeTab === 'manual' && itinerary && (
            <div className="itinerary-cards">
              {/* Flight Cards */}
              <h3>Flight Options</h3>
              <div className="cards-container">
                {itinerary.flights.map((flight, index) => (
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

                    {flight.type && (
                      <p>
                        <strong>Type:</strong> {flight.type}
                      </p>
                    )}
                    {flight.layover && flight.layover !== 'None' && (
                      <p>
                        <strong>Layover:</strong> {flight.layover}
                      </p>
                    )}
                    {flight.airline && flight.airline.length > 0 && (
                      <p>
                        <strong>Airline(s):</strong> {flight.airline.join(', ')}
                      </p>
                    )}
                    {flight.confidence && (
                      <p>
                        <strong>Confidence:</strong> {flight.confidence}
                      </p>
                    )}
                    {flight.miles && (
                      <p>
                        <strong>Miles:</strong> {flight.miles}
                      </p>
                    )}
                    {flight.source_of_route && (
                      <p>
                        <strong>Source of Route:</strong>{' '}
                        <a href={flight.source_of_route} target="_blank" rel="noopener noreferrer">
                          {flight.source_of_route}
                        </a>
                      </p>
                    )}
                    {flight.carbon_emission !== NaN && flight.carbon_emission !== 0 && (
                      <p>
                        <strong>Carbon Emissions:</strong> {flight.carbon_emission.toFixed(2)} kg CO₂
                      </p>
                    )}
                  </div>
                ))}
              </div>

              {/* Hotel Cards */}
              <h3>Hotel Options</h3>
              <div className="cards-container">
                {itinerary.hotels.map((hotel, index) => (
                  <div
                    key={index}
                    className="card hotel-card"
                    onClick={() => handleCardClick(hotel, 'hotel')}
                  >
                    <div className="card-icon">
                      <FaBed />
                    </div>
                    <h4>{hotel.name}</h4>
                    <p>
                      <FaMapMarkerAlt /> {hotel.location}
                    </p>
                    {hotel.hotel_type && <p>
                      <strong>Type:</strong> {hotel.hotel_type}
                    </p>}
                    {hotel.carbon_emission && <p>
                      <strong>Carbon Emissions:</strong> {hotel.carbon_emission.toFixed(2)} kg CO₂
                    </p>}
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