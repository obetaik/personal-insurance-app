// authConstants.js - for constants and utility functions
export const AUTH_CONFIG = {
  audience: import.meta.env.VITE_AUTH0_AUDIENCE,
  // Add any other auth constants here
};

// Utility function to get token
export const getStoredToken = () => {
  return localStorage.getItem('access_token');
};

// Any other auth-related helper functions
export const clearStoredToken = () => {
  localStorage.removeItem('access_token');
};
