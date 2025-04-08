import React, { useState, useMemo, useEffect } from 'react';
import { 
  FaPlane, FaCar, FaHotel, FaSearch, FaLeaf, FaSun, FaMoon, 
  FaMapMarkerAlt, FaBed, FaTimes, FaUpload, FaCheckCircle, FaInfoCircle 
} from 'react-icons/fa';
import './App.css';
import { Box, Button, CardContent, IconButton, Paper, Typography, Autocomplete, TextField } from '@mui/material';
import { UploadFile as UploadFileIcon, Delete as DeleteIcon, InsertDriveFile as FileIcon } from '@mui/icons-material';
import { useTheme, ThemeProvider, createTheme } from "@mui/material/styles";
import { ModernSourceAutocomplete, ModernDestinationAutocomplete } from './Airportdropdown';

const documentationLink = "https://docs.google.com/document/d/1XQJtfGitnU3eroQZ05l4XqRAbrhCVhYOXlyj1uyLo5k/edit?tab=t.0#heading=h.pp9o87y0cd36";

const TravelForm = () => {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [result, setResult] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCard, setSelectedCard] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [calculatedMiles, setCalculatedMiles] = useState(null);
  const [calculatedEmissions, setCalculatedEmissions] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('manual');
  const [airportCodes, setAirportCodes] = useState([]);
  const [airportsLoading, setAirportsLoading] = useState(false);

  // Determine whether to show the Upload tab based on an environment variable
  const showUploadTab = import.meta.env.VITE_APP_SHOW_UPLOAD_TAB === "true";

  // Force activeTab to manual if upload tab is disabled
  useEffect(() => {
    if (!showUploadTab) {
      console.log(showUploadTab)
      setActiveTab('manual');
    }
  }, [showUploadTab, activeTab]);

  // Create a dynamic theme that updates on toggle
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? "dark" : "light",
        },
      }),
    [darkMode]
  );

  // Fetch airport codes on component mount
  useEffect(() => {
    const fetchAirportCodes = async () => {
      setAirportsLoading(true);
      try {
        const airportsUrl = import.meta.env.VITE_APP_AIRPORTS_URL;
        const response = await fetch(airportsUrl);
        
        if (!response.ok) {
          // If API is not available, use sample dataset
          const sampleAirportCodes = [
            'ATL', 'DFW', 'DEN', 'ORD', 'LAX', 'JFK', 'LAS', 'MCO', 'MIA', 'SEA', 
            'PHX', 'EWR', 'SFO', 'IAH', 'BOS', 'FLL', 'MSP', 'CLT', 'LGA', 'DTW'
          ];
          setAirportCodes(sampleAirportCodes);
          console.log('Using sample airport codes');
          return;
        }
        
        const data = await response.json();
        
        // Parse the nested response structure
        if (data.response && 
            data.response.status === "success" && 
            Array.isArray(data.response.iata_codes)) {
          // Filter out duplicate airport codes before setting state
          const uniqueAirportCodes = [...new Set(data.response.iata_codes)];
          setAirportCodes(uniqueAirportCodes);
          console.log(`Loaded ${uniqueAirportCodes.length} unique airport codes out of ${data.response.count}`);
        } else {
          console.error('Unexpected API response format:', data);
          throw new Error('Invalid API response format');
        }
      } catch (err) {
        console.error('Error fetching airport codes:', err);
        // Fallback to sample data
        const sampleAirportCodes = [
          'ATL', 'DFW', 'DEN', 'ORD', 'LAX', 'JFK', 'LAS', 'MCO', 'MIA', 'SEA'
        ];
        setAirportCodes(sampleAirportCodes);
      } finally {
        setAirportsLoading(false);
      }
    };

    fetchAirportCodes();
  }, []);

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

      const data = await response.json();
      console.log(data);

      if (!data.answer) {
        throw new Error('Invalid response format from API');
      }

      const outerParsed = data.answer;
      console.log(outerParsed);
      setItinerary(outerParsed);
    } catch (err) {
      console.log(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleCardClick = (cardData, type) => {
    setSelectedCard({ ...cardData, type });
  };

  const closeDetailedCard = () => {
    setSelectedCard(null);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];

    if (!file) {
      setError("No file selected.");
      return;
    }

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
    <ThemeProvider theme={theme}>
      <div className={`app-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
        {/* Header */}
        <header className="header">
          <div className="logo">
            <FaLeaf className="logo-icon" />
            <span>Sustainable Travel Planner</span>
          </div>
          <button onClick={toggleDarkMode} className="mode-toggle">
            {darkMode ? <FaSun /> : <FaMoon />}
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
          {/* Wrapper with side notes */}
          <div
            className="form-and-notes"
            style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', gap: '20px' }}
          >
            {/* Left Side Note */}
            <Paper
              elevation={3}
              sx={{
                flex: '1',
                maxWidth: '250px',
                p: 2,
                borderRadius: 2,
                backgroundColor: theme.palette.mode === "dark" ? theme.palette.grey[900] : theme.palette.grey[100],
              }}
            >
              <Box display="flex" alignItems="center" mb={1}>
                <FaInfoCircle style={{ marginRight: '8px', fontSize: '1.8rem', color: theme.palette.primary.main }} />
                <Typography variant="h6">About This Tool</Typography>
              </Box>
              <Typography variant="body2" mb={2}>
                Want to know how we came up with this innovative travel planner? Learn about our research, methodology, and inspiration behind the tool.
              </Typography>
              <Button variant="outlined" href={documentationLink} target="_blank" rel="noopener noreferrer">
                Learn More
              </Button>
            </Paper>

            {/* Form Container */}
            <div className="travel-form-container" style={{ flex: '2', minWidth: '300px' }}>
              <h2>Sustainable Travel Planner</h2>
              <p className="subtitle">Enter your details to plan your trip</p>

              {/* Icons Section */}
              <div className="icons-section">
                <div className="icon-item">
                  <FaPlane className="icon" />
                  <span>Flights</span>
                </div>
                <div className="icon-item">
                  <FaHotel className="icon" />
                  <span>Hotels</span>
                </div>
              </div>

              {showUploadTab && (<div className="tabs">
                <button className={activeTab === 'manual' ? 'active' : ''} onClick={() => handleTabChange('manual')}>
                  Manual Input
                </button>
                {showUploadTab && (
                  <button className={activeTab === 'upload' ? 'active' : ''} onClick={() => handleTabChange('upload')}>
                    Upload File
                  </button>
                )}
              </div>)}

              {(activeTab === 'manual' || !showUploadTab) ? (
                <form onSubmit={handleSubmit}>
                  {/* SOURCE AIRPORT FIELD */}
                  <div className="input-group">
                    <label htmlFor="source" className="modern-label">
                      <FaPlane className="input-icon" /> Origin Airport
                    </label>
                    <ModernSourceAutocomplete 
                      source={source} 
                      setSource={setSource} 
                      airportCodes={airportCodes} 
                      airportsLoading={airportsLoading} 
                      theme={theme} 
                    />
                  </div>
                  
                  {/* DESTINATION AIRPORT FIELD */}
                  <div className="input-group">
                    <label htmlFor="destination" className="modern-label">
                      <FaPlane className="input-icon" style={{ transform: 'rotate(45deg)' }} /> Destination Airport
                    </label>
                    <ModernDestinationAutocomplete 
                      destination={destination} 
                      setDestination={setDestination} 
                      airportCodes={airportCodes} 
                      airportsLoading={airportsLoading} 
                      theme={theme} 
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
                        borderLeft: `4px solid ${theme.palette.mode === "dark" ? "#3498db" : "#007bff"}`,
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



              {activeTab === 'manual' && result && <p className="result">{result}</p>}

              {error && <p className="error-message">{error}</p>}

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

              {activeTab === 'manual' && itinerary && (
                <div className="itinerary-cards">
                  <h3>Flight Options</h3>
                  <div className="cards-container">
                    {itinerary.flights.map((flight, index) => (
                      <div
                        key={index}
                        className={`card flight-card ${index === 0 ? 'highlight-card' : ''}`}
                        onClick={() => handleCardClick(flight, 'flight')}
                      >
                        {index === 0 && (
                          <div className="badge most-sustainable-badge">Most Sustainable</div>
                        )}
                        <div className="card-icon">
                          <FaPlane />
                        </div>
                        <h4>{flight.source} → {flight.destination}</h4>
                        {flight.type && <p><strong>Type:</strong> {flight.type}</p>}
                        {flight.layover && flight.layover !== 'None' && (
                          <p><strong>Layover:</strong> {flight.layover}</p>
                        )}
                        {flight.airline && (
                          <p><strong>Airline(s):</strong> {Array.isArray(flight.airline) ? flight.airline.join(', ') : flight.airline}</p>
                        )}
                        {flight.confidence && <p><strong>Confidence:</strong> {flight.confidence}</p>}
                        {flight.miles && <p><strong>Miles:</strong> {flight.miles}</p>}
                        {flight.source_of_route && (
                          <p>
                            <strong>Source of Route:</strong>{' '}
                            {flight.source_of_route === "DB" ? (
                              flight.source_of_route
                            ) : (
                              <a
                                href={flight.source_of_route}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {flight.source_of_route}
                              </a>
                            )}
                          </p>
                        )}
                        {flight.carbon_emission !== NaN && flight.carbon_emission !== 0 && (
                          <p><strong>Carbon Emissions:</strong> {(flight.carbon_emission / 1e4).toFixed(2)} kg CO₂</p>
                        )}
                      </div>
                    ))}
                  </div>

                  <h3>Hotel Options</h3>
                  <div className="cards-container">
                    {itinerary.hotels.map((hotel, index) => (
                      <div
                        key={index}
                        className={`card hotel-card ${index === 0 ? 'highlight-card' : ''}`}
                        onClick={() => handleCardClick(hotel, 'hotel')}
                      >
                        {index === 0 && (
                          <div className="badge most-sustainable-badge">Most Sustainable</div>
                        )}
                        <div className="card-icon">
                          <FaBed />
                        </div>
                        <h4>{hotel.name}</h4>
                        <p><FaMapMarkerAlt /> {hotel.location}</p>
                        {hotel.hotel_type && <p><strong>Type:</strong> {hotel.hotel_type}</p>}
                        {hotel.carbon_emission && <p><strong>Carbon Emissions:</strong> {hotel.carbon_emission.toFixed(2)} kg CO₂ / day</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Side Note */}
            <Paper
              elevation={3}
              sx={{
                flex: '1',
                maxWidth: '250px',
                p: 2,
                borderRadius: 2,
                backgroundColor: theme.palette.mode === "dark" ? theme.palette.grey[900] : theme.palette.grey[100],
              }}
            >
              <Box display="flex" alignItems="center" mb={1}>
                <FaInfoCircle style={{ marginRight: '8px', fontSize: '1.8rem', color: theme.palette.secondary.main }} />
                <Typography variant="h6">Disclaimer</Typography>
              </Box>
              <Typography variant="body2">
                Please note that some recommendations are generated by AI and might not always be 100% accurate. Verify critical details before finalizing your plans.
              </Typography>
            </Paper>
          </div>
        </section>

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
                    <strong>Carbon Emissions:</strong> {(selectedCard.carbon_emission / 1e4).toFixed(2)} kg CO₂
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
                    <strong>Carbon Emissions:</strong> {selectedCard.carbon_emission.toFixed(2)} kg CO₂ / day
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </ThemeProvider>
  );
};

export default TravelForm;