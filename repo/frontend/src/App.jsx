// frontend/src/App.jsx
import { useEffect } from 'react';
import { AppProvider, useAppContext } from './contexts/AppContext';
import DashboardLayout from './DashboardLayout';
import DataBrowser from './DataBrowser';
import ChangeRequests from './ChangeRequests';
import PredefinedQueries from './PredefinedQueries';
import Settings from './Settings';
import LoginPage from './LoginPage';
import './App.css';

function AppContent() {
  const { isAuthenticated, isAdmin, appState, updateAppState } = useAppContext();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

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
