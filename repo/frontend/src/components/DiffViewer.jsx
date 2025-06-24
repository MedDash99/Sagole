import React from 'react';

const DiffViewer = ({ oldValues, newValues }) => {
  // Ensure values are parsed if they are strings
  const parsedOld = typeof oldValues === 'string' ? JSON.parse(oldValues) : oldValues || {};
  const parsedNew = typeof newValues === 'string' ? JSON.parse(newValues) : newValues || {};

  const allKeys = new Set([
    ...Object.keys(parsedOld),
    ...Object.keys(parsedNew)
  ]);

  const renderValue = (value) => {
    if (value === null || value === undefined) {
      return <span className="diff-null">null</span>;
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  const renderDiffRow = (key) => {
    const oldValue = parsedOld[key];
    const newValue = parsedNew[key];
    const isAdded = oldValue === undefined;
    const isRemoved = newValue === undefined;
    const isModified = !isAdded && !isRemoved && JSON.stringify(oldValue) !== JSON.stringify(newValue);

    let indicator = <span className="indicator-space"></span>;
    let rowClass = 'diff-row';

    if (isAdded) {
      indicator = <span className="indicator added">+</span>;
      rowClass += ' added';
    } else if (isRemoved) {
      indicator = <span className="indicator removed">-</span>;
      rowClass += ' removed';
    } else if (isModified) {
      indicator = <span className="indicator modified">~</span>;
      rowClass += ' modified';
    }

    return (
      <div key={key} className={rowClass}>
        {indicator}
        <div className="diff-key">{key}:</div>
        <div className="diff-values">
          {isModified ? (
            <>
              <div className="diff-old">{renderValue(oldValue)}</div>
              <div className="diff-arrow">→</div>
              <div className="diff-new">{renderValue(newValue)}</div>
            </>
          ) : (
            <div className="diff-new">{renderValue(newValue)}</div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="diff-viewer-gitlens">
      <div className="diff-header">
        <span>FIELD</span>
        <span>CHANGE</span>
      </div>
      <div className="diff-content">
        {Array.from(allKeys).map(renderDiffRow)}
      </div>
    </div>
  );
};

export default DiffViewer; 