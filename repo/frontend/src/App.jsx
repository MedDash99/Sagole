// frontend/src/App.jsx
import { useEffect } from 'react';
import { AppProvider, useAppContext } from './contexts/AppContext';
import DashboardLayout from './DashBoardLayout';
import DataBrowser from './DataBrowser';
import ChangeRequests from './ChangeRequests';
import PredefinedQueries from './PredefinedQueries';
import Settings from './Settings';
import './App.css';

function AppContent() {
  const { isAuthenticated, isAdmin, appState, updateAppState } = useAppContext();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      // For now, we'll simulate authentication
      // In a real app, you'd redirect to a login page
      console.log('User not authenticated');
    }
  }, [isAuthenticated]);

  // This function will render the correct component based on the active view
  const renderActiveView = () => {
    switch (appState.activeView) {
      case 'dataBrowser':
        return <DataBrowser />;
      case 'changeRequests':
        return isAdmin ? <ChangeRequests /> : <div>Access denied. Admin privileges required.</div>;
      case 'predefinedQueries':
        return <PredefinedQueries />;
      case 'settings':
        return <Settings />;
      default:
        return <DataBrowser />;
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="login-placeholder">
        <h1>Database Admin Panel</h1>
        <p>Please log in to continue</p>
        <button onClick={() => {
          // Simulate login for demo purposes
          localStorage.setItem('authToken', 'demo-token');
          localStorage.setItem('userRole', 'admin');
          window.location.reload();
        }}>
          Demo Login (Admin)
        </button>
      </div>
    );
  }

  return (
    <DashboardLayout 
      activeView={appState.activeView} 
      setActiveView={(view) => updateAppState({ activeView: view })}
    >
      {renderActiveView()}
    </DashboardLayout>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
