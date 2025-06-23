import React from 'react';

const DiffViewer = ({ oldValues, newValues }) => {
  const allKeys = new Set([
    ...Object.keys(oldValues || {}),
    ...Object.keys(newValues || {})
  ]);

  const renderDiffRow = (key) => {
    const oldValue = oldValues?.[key];
    const newValue = newValues?.[key];
    const hasChanged = oldValue !== newValue;

    const formatValue = (value) => {
      if (value === null || value === undefined) {
        return 'null';
      }
      if (typeof value === 'object') {
        return JSON.stringify(value, null, 2);
      }
      return String(value);
    };

    return (
      <div key={key} className={`diff-row ${hasChanged ? 'changed' : ''}`}>
        <div className="diff-key">{key}:</div>
        <div className="diff-values">
          <div className={`diff-old ${hasChanged ? 'removed' : ''}`}>
            {formatValue(oldValue)}
          </div>
          <div className={`diff-new ${hasChanged ? 'added' : ''}`}>
            {formatValue(newValue)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="diff-viewer">
      <div className="diff-header">
        <div className="diff-title">Changes</div>
        <div className="diff-labels">
          <span className="diff-label removed">Old Values</span>
          <span className="diff-label added">New Values</span>
        </div>
      </div>
      <div className="diff-content">
        {Array.from(allKeys).map(renderDiffRow)}
      </div>
    </div>
  );
};

export default DiffViewer; 