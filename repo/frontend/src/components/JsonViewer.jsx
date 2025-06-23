import React, { useState, useRef, useEffect } from 'react';

const JsonViewer = ({ data, label = "View JSON" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const buttonRef = useRef(null);
  const popoverRef = useRef(null);

  // Check if the data is JSON
  const isJson = (value) => {
    if (typeof value === 'object' && value !== null) {
      return true;
    }
    if (typeof value === 'string') {
      try {
        JSON.parse(value);
        return true;
      } catch {
        return false;
      }
    }
    return false;
  };

  // Format JSON for display
  const formatJson = (value) => {
    if (typeof value === 'string') {
      try {
        return JSON.stringify(JSON.parse(value), null, 2);
      } catch {
        return value;
      }
    }
    return JSON.stringify(value, null, 2);
  };

  // Position the popover relative to the button
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect();
      const popoverWidth = 400;
      const popoverHeight = 300;
      
      let left = buttonRect.left;
      let top = buttonRect.bottom + 5;
      
      // Adjust if popover would go off screen
      if (left + popoverWidth > window.innerWidth) {
        left = window.innerWidth - popoverWidth - 10;
      }
      if (top + popoverHeight > window.innerHeight) {
        top = buttonRect.top - popoverHeight - 5;
      }
      
      setPosition({ top, left });
    }
  }, [isOpen]);

  // Close popover when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target) &&
          buttonRef.current && !buttonRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  if (!isJson(data)) {
    return <span>{String(data)}</span>;
  }

  return (
    <div className="json-viewer">
      <button
        ref={buttonRef}
        className="json-viewer-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Click to view JSON data"
      >
        {label}
      </button>
      
      {isOpen && (
        <div
          ref={popoverRef}
          className="json-popover"
          style={{
            position: 'fixed',
            top: position.top,
            left: position.left,
            zIndex: 1000
          }}
        >
          <div className="json-popover-header">
            <span>JSON Data</span>
            <button
              className="json-popover-close"
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
          </div>
          <div className="json-popover-content">
            <pre>{formatJson(data)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default JsonViewer; 