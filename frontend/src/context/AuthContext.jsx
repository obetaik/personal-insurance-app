/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect, useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { AUTH_CONFIG, clearStoredToken } from './authConstants';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const auth0 = useAuth0();
  const { getAccessTokenSilently, isAuthenticated } = auth0;

  const getToken = useCallback(async () => {
    if (isAuthenticated) {
      try {
        const audience = AUTH_CONFIG.audience;
        if (!audience) {
          console.error('VITE_AUTH0_AUDIENCE environment variable is not set');
          return;
        }
        
        console.log('🔑 Attempting to get access token...');
        const token = await getAccessTokenSilently({
          authorizationParams: {
            audience: audience,
          },
        });
        
        if (token) {
          localStorage.setItem('access_token', token);
          console.log('✅ Access token stored successfully');
          console.log('Token preview:', token.substring(0, 20) + '...');
        } else {
          console.warn('⚠️ Token received but empty');
        }
      } catch (error) {
        console.error('❌ Error getting access token:', error);
        console.error('Error details:', {
          message: error.message,
          error: error.error,
          errorDescription: error.error_description
        });
        clearStoredToken();
      }
    } else {
      console.log('🔓 Not authenticated, clearing token');
      clearStoredToken();
    }
  }, [isAuthenticated, getAccessTokenSilently]);

  useEffect(() => {
    getToken();
  }, [getToken]);

  useEffect(() => {
    if (!isAuthenticated) return;
    
    const interval = setInterval(() => {
      getToken();
    }, 50 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [isAuthenticated, getToken]);

  const value = {
    ...auth0,
    getToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};