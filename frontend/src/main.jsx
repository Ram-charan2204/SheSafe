import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

window.addEventListener("scroll", () => {
  if (window.scrollY > 10) {
    document.body.classList.add("scrolled");
  } else {
    document.body.classList.remove("scrolled");
  }
});

createRoot(document.getElementById('root')).render(
  
  <StrictMode>
    <App />
  </StrictMode>,
)
