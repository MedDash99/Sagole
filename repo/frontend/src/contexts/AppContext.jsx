import { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [currentEnvironment, setCurrentEnvironment] = useState('dev');
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [appState, setAppState] = useState({
    activeView: 'dataBrowser',
    selectedTable: null,
    tableData: [],
    currentPage: 1,
    filters: []
  });

  // Check authentication status on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const userRole = localStorage.getItem('userRole');
    
    if (token) {
      setIsAuthenticated(true);
      setUser({ role: userRole || 'user' });
      setIsAdmin(userRole === 'admin');
    }
  }, []);

  const login = (token, role) => {
    // In a real app, you would verify the token and fetch user info from the backend
    localStorage.setItem('authToken', token);
    localStorage.setItem('userRole', role);
    setIsAuthenticated(true);
    setUser({ role });
    setIsAdmin(role === 'admin');
    // Reset app state to clean defaults
    setAppState({
      activeView: 'dataBrowser',
      selectedTable: null,
      tableData: [],
      currentPage: 1,
      filters: []
    });
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    setIsAuthenticated(false);
    setUser(null);
    setIsAdmin(false);
    
    // Reset all state to clean defaults
    setCurrentEnvironment('dev');
    setAppState({
      activeView: 'dataBrowser',
      selectedTable: null,
      tableData: [],
      currentPage: 1,
      filters: []
    });
    
    // Redirect to login page
    window.location.href = '/';
  };

  const changeEnvironment = (newEnvironment) => {
    setCurrentEnvironment(newEnvironment);
    // Reset table-related state when environment changes
    setAppState(prev => ({
      ...prev,
      selectedTable: null,
      tableData: [],
      currentPage: 1,
      filters: []
    }));
  };

  const updateAppState = (updates) => {
    setAppState(prev => ({ ...prev, ...updates }));
  };

  const value = {
    currentEnvironment,
    changeEnvironment,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    appState,
    updateAppState,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}; 