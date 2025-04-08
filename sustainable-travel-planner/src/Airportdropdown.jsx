import React from 'react';
import { Autocomplete, TextField, Box, CircularProgress, Typography } from '@mui/material';
import FlightIcon from '@mui/icons-material/Flight';
import LocationOnIcon from '@mui/icons-material/LocationOn';

// Modern Source Autocomplete component
const ModernSourceAutocomplete = ({ source, setSource, airportCodes, airportsLoading, theme }) => {
  return (
    <Autocomplete
      id="source-autocomplete"
      options={airportCodes}
      loading={airportsLoading}
      value={source}
      onChange={(event, newValue) => {
        setSource(newValue || '');
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder="Enter airport code (e.g., JFK, LAX)"
          required
          variant="outlined"
          fullWidth
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <>
                <Box display="flex" alignItems="center" mr={1}>
                  <FlightIcon sx={{ color: '#3498db' }} />
                </Box>
                {params.InputProps.startAdornment}
              </>
            ),
            endAdornment: (
              <>
                {airportsLoading ? <CircularProgress color="primary" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            )
          }}
        />
      )}
      renderOption={(props, option) => {
        const { key, ...otherProps } = props;
        return (
          <Box
            component="li"
            key={key}
            {...otherProps}
            sx={{
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.2s ease',
              '&:hover': {
                backgroundColor:
                  theme.palette.mode === 'dark'
                    ? 'rgba(52, 152, 219, 0.2)'
                    : 'rgba(52, 152, 219, 0.1)',
              },
            }}
          >
            <LocationOnIcon
              sx={{
                color: '#3498db',
                mr: 1,
                fontSize: '1.2rem',
              }}
            />
            <Box>
              <Typography variant="body1" fontWeight="500">
                {option}
              </Typography>
            </Box>
          </Box>
        );
      }}
      noOptionsText={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '10px',
          }}
        >
          <Typography variant="body1" color="text.secondary">
            No matching airports
          </Typography>
        </Box>
      }
      filterOptions={(options, state) => {
        const inputValue = state.inputValue.trim().toUpperCase();
        if (inputValue.length === 0) return [];
        return [...new Set(options.filter((option) => option.includes(inputValue)))].slice(0, 10);
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: '16px',
          transition: 'all 0.3s ease',
          backgroundColor:
            theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'white',
          padding: '4px 4px 4px 8px',
          border:
            theme.palette.mode === 'dark'
              ? '1px solid rgba(255, 255, 255, 0.12)'
              : '1px solid rgba(0, 0, 0, 0.12)',
          boxShadow: '0 2px 6px rgba(0, 0, 0, 0.05)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            borderColor:
              theme.palette.mode === 'dark'
                ? 'rgba(52, 152, 219, 0.5)'
                : 'rgba(52, 152, 219, 0.3)',
          },
          '&.Mui-focused': {
            boxShadow: '0 4px 20px rgba(52, 152, 219, 0.25)',
            borderColor: '#3498db',
          },
        },
        '& .MuiInputBase-input': {
          padding: '12px 4px 12px 8px',
        },
        '& .MuiAutocomplete-endAdornment': {
          right: '12px',
        },
        '& .MuiAutocomplete-popupIndicator': {
          color:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.5)'
              : 'rgba(0, 0, 0, 0.5)',
        },
        '& .MuiAutocomplete-clearIndicator': {
          color:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.5)'
              : 'rgba(0, 0, 0, 0.5)',
        },
        mb: 3,
      }}
    />
  );
};

// Modern Destination Autocomplete component
const ModernDestinationAutocomplete = ({ destination, setDestination, airportCodes, airportsLoading, theme }) => {
  return (
    <Autocomplete
      id="destination-autocomplete"
      options={airportCodes}
      loading={airportsLoading}
      value={destination}
      onChange={(event, newValue) => {
        setDestination(newValue || '');
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          placeholder="Enter airport code (e.g., LHR, CDG)"
          required
          variant="outlined"
          fullWidth
          InputProps={{
            ...params.InputProps,
            startAdornment: (
              <>
                <Box display="flex" alignItems="center" mr={1}>
                  <FlightIcon
                    sx={{ color: '#e74c3c', transform: 'rotate(45deg)' }}
                  />
                </Box>
                {params.InputProps.startAdornment}
              </>
            ),
            endAdornment: (
              <>
                {airportsLoading ? <CircularProgress color="error" size={20} /> : null}
                {params.InputProps.endAdornment}
              </>
            ),
          }}
        />
      )}
      renderOption={(props, option) => {
        const { key, ...otherProps } = props;
        return (
          <Box
            component="li"
            key={key}
            {...otherProps}
            sx={{
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.2s ease',
              '&:hover': {
                backgroundColor:
                  theme.palette.mode === 'dark'
                    ? 'rgba(231, 76, 60, 0.2)'
                    : 'rgba(231, 76, 60, 0.1)',
              },
            }}
          >
            <LocationOnIcon
              sx={{
                color: '#e74c3c',
                mr: 1,
                fontSize: '1.2rem',
              }}
            />
            <Box>
              <Typography variant="body1" fontWeight="500">
                {option}
              </Typography>
            </Box>
          </Box>
        );
      }}
      noOptionsText={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '10px',
          }}
        >
          <Typography variant="body1" color="text.secondary">
            No matching airports
          </Typography>
        </Box>
      }
      filterOptions={(options, state) => {
        const inputValue = state.inputValue.trim().toUpperCase();
        if (inputValue.length === 0) return [];
        return [...new Set(options.filter((option) => option.includes(inputValue)))].slice(0, 10);
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: '16px',
          transition: 'all 0.3s ease',
          backgroundColor:
            theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'white',
          padding: '4px 4px 4px 8px',
          border:
            theme.palette.mode === 'dark'
              ? '1px solid rgba(255, 255, 255, 0.12)'
              : '1px solid rgba(0, 0, 0, 0.12)',
          boxShadow: '0 2px 6px rgba(0, 0, 0, 0.05)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            borderColor:
              theme.palette.mode === 'dark'
                ? 'rgba(231, 76, 60, 0.5)'
                : 'rgba(231, 76, 60, 0.3)',
          },
          '&.Mui-focused': {
            boxShadow: '0 4px 20px rgba(231, 76, 60, 0.25)',
            borderColor: '#e74c3c',
          },
        },
        '& .MuiInputBase-input': {
          padding: '12px 4px 12px 8px',
        },
        '& .MuiAutocomplete-endAdornment': {
          right: '12px',
        },
        '& .MuiAutocomplete-popupIndicator': {
          color:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.5)'
              : 'rgba(0, 0, 0, 0.5)',
        },
        '& .MuiAutocomplete-clearIndicator': {
          color:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.5)'
              : 'rgba(0, 0, 0, 0.5)',
        },
        mb: 3,
      }}
    />
  );
};

export { ModernSourceAutocomplete, ModernDestinationAutocomplete };