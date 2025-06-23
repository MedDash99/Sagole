// frontend/src/DashBoardLayout.jsx
import React, { useState } from 'react';
import { useAppContext } from './contexts/AppContext';

// SVG Icons for the sidebar navigation
const DataBrowserIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3"width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>;
const PredefinedQueriesIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>;
const ChangeRequestsIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="m9 12 2 2 4-4"></path></svg>;
const SettingsIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09A1.65 1.65 0 0 0 15.4 4.6a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09A1.65 1.65 0 0 0-1.51 1z"></path></svg>;
const ChevronDownIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>;

const environments = ['dev', 'test', 'stage', 'prod'];

export default function DashboardLayout({ children, activeView, setActiveView }) {
  const { currentEnvironment, changeEnvironment, user, logout, isAdmin } = useAppContext();
  const [showEnvDropdown, setShowEnvDropdown] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);

  const navItems = [
    { name: 'Data Browser', key: 'dataBrowser', icon: <DataBrowserIcon />, adminOnly: false },
    { name: 'Predefined Queries', key: 'predefinedQueries', icon: <PredefinedQueriesIcon />, adminOnly: false },
    { name: 'Change Requests', key: 'changeRequests', icon: <ChangeRequestsIcon />, adminOnly: true },
    { name: 'Settings', key: 'settings', icon: <SettingsIcon />, adminOnly: false },
  ];

  const handleEnvironmentChange = (env) => {
    changeEnvironment(env);
    setShowEnvDropdown(false);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">{currentEnvironment}</div>
        <nav className="sidebar-nav">
          {navItems.map(item => {
            // Hide admin-only items for non-admin users
            if (item.adminOnly && !isAdmin) return null;
            
            return (
              <button
                key={item.key}
                onClick={() => setActiveView(item.key)}
                className={`nav-button ${activeView === item.key ? 'active' : ''}`}
              >
                {item.icon}
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main content area */}
      <div className="content-wrapper">
        {/* Top bar */}
        <header className="header">
          <div className="environment-selector">
            <button 
              className="env-button"
              onClick={() => setShowEnvDropdown(!showEnvDropdown)}
            >
              <span>{currentEnvironment}</span>
              <ChevronDownIcon />
            </button>
            {showEnvDropdown && (
              <div className="env-dropdown">
                {environments.map(env => (
                  <button
                    key={env}
                    onClick={() => handleEnvironmentChange(env)}
                    className={`env-option ${currentEnvironment === env ? 'active' : ''}`}
                  >
                    {env}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="user-profile">
            <div className="user-avatar">A</div>
            <div className="user-details">
              <div className="font-medium">{user?.role || 'User'}</div>
              <div className="text-gray-500">{user?.role || 'User'}</div>
            </div>
            <button 
              className="profile-button"
              onClick={() => setShowProfileDropdown(!showProfileDropdown)}
            >
              <ChevronDownIcon />
            </button>
            {showProfileDropdown && (
              <div className="profile-dropdown">
                <button onClick={handleLogout} className="profile-option">
                  Log out
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Content */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
