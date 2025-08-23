import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Security: Disable right-click context menu
document.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  return false;
});

// Security: Disable keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Disable Ctrl+S, Ctrl+P, Ctrl+U, F12, Ctrl+Shift+I, Ctrl+Shift+J
  if (
    (e.ctrlKey && (e.key === 's' || e.key === 'p' || e.key === 'u')) ||
    e.key === 'F12' ||
    (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J'))
  ) {
    e.preventDefault();
    return false;
  }
});

// Security: Disable developer tools
setInterval(() => {
  const devtools = /./;
  devtools.toString = function() {
    this.opened = true;
  }
  console.log('%c', devtools);
  console.clear();
}, 1000);

// Security: Disable drag and drop
document.addEventListener('dragstart', (e) => {
  e.preventDefault();
  return false;
});

// Security: Disable text selection
document.addEventListener('selectstart', (e) => {
  e.preventDefault();
  return false;
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
