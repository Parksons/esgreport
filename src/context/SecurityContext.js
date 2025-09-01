import React, { createContext, useContext, useState, useEffect } from 'react';

const SecurityContext = createContext();

export const useSecurity = () => {
  const context = useContext(SecurityContext);
  if (!context) {
    throw new Error('useSecurity must be used within a SecurityProvider');
  }
  return context;
};

export const SecurityProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);
  const [sessionTimeout, setSessionTimeout] = useState(null);

  // Check authentication status on mount
  useEffect(() => {
    const authStatus = localStorage.getItem('isAuthenticated');
    const userInfo = localStorage.getItem('userData');
    
    if (authStatus === 'true' && userInfo) {
      const userData = JSON.parse(userInfo);
      
      // Verify token with backend
      verifyTokenWithServer(userData.accessToken).then(isValid => {
        if (isValid) {
          setIsAuthenticated(true);
          setUserData(userData);
          
          // Set session timeout (30 minutes)
          const timeout = setTimeout(() => {
            logout();
          }, 30 * 60 * 1000);
          
          setSessionTimeout(timeout);
        } else {
          // Token is invalid, clear storage
          logout();
        }
      }).catch(() => {
        // Error verifying token, clear storage
        logout();
      });
    }
  }, []);

  // Verify token with backend
  const verifyTokenWithServer = async (token) => {
    try {
      const API_BASE_URL = 'https://esgreport-production.up.railway.app/';
      const response = await fetch(`${API_BASE_URL}/verify-token`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      return response.ok;
    } catch (error) {
      console.error('Error verifying token:', error);
      return false;
    }
  };

  // Clear timeout on unmount
  useEffect(() => {
    return () => {
      if (sessionTimeout) {
        clearTimeout(sessionTimeout);
      }
    };
  }, [sessionTimeout]);

  // Login function
  const login = (userInfo) => {
    setIsAuthenticated(true);
    setUserData(userInfo);
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('userData', JSON.stringify(userInfo));
    
    // Reset session timeout
    if (sessionTimeout) {
      clearTimeout(sessionTimeout);
    }
    
    const timeout = setTimeout(() => {
      logout();
    }, 30 * 60 * 1000);
    
    setSessionTimeout(timeout);
  };

  // Logout function
  const logout = async () => {
    // Call backend logout endpoint if we have a token
    if (userData?.accessToken) {
      try {
        // const API_BASE_URL = 'https://esgreport-production.up.railway.app/';
        const API_BASE_URL = 'http://localhost:8000';
        await fetch(`${API_BASE_URL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${userData.accessToken}`,
            'Content-Type': 'application/json',
          },
        });
      } catch (error) {
        console.error('Error logging out from server:', error);
      }
    }
    
    setIsAuthenticated(false);
    setUserData(null);
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userData');
    
    if (sessionTimeout) {
      clearTimeout(sessionTimeout);
      setSessionTimeout(null);
    }
  };

  // Extend session
  const extendSession = () => {
    if (sessionTimeout) {
      clearTimeout(sessionTimeout);
    }
    
    const timeout = setTimeout(() => {
      logout();
    }, 30 * 60 * 1000);
    
    setSessionTimeout(timeout);
  };

  // Security check function
  const securityCheck = () => {
    // Additional security checks can be added here
    return isAuthenticated;
  };

  const value = {
    isAuthenticated,
    userData,
    login,
    logout,
    extendSession,
    securityCheck
  };

  return (
    <SecurityContext.Provider value={value}>
      {children}
    </SecurityContext.Provider>
  );
};
