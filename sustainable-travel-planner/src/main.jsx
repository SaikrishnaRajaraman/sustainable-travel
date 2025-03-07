import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import TravelForm from './TravelForm.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <TravelForm />
  </StrictMode>,
)

