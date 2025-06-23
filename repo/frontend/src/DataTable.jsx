import { useState } from 'react';
import axios from 'axios';
import JsonViewer from './components/JsonViewer';

const API_URL = 'http://localhost:8000/api/v1';

const SortIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 15l5 5 5-5M7 9l5-5 5 5" />
    </svg>
);

const Pagination = ({ currentPage, totalPages, totalRecords, onPageChange }) => {
  const startRecord = (currentPage - 1) * 10 + 1;
  const endRecord = Math.min(currentPage * 10, totalRecords);

  return (
    <div className="pagination-controls">
      <span>{startRecord}-{endRecord} of {totalRecords}</span>
      <button 
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className="pagination-btn"
      >
        &lt;
      </button>
      <span className="page-info">Page {currentPage} of {totalPages}</span>
      <button 
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="pagination-btn"
      >
        &gt;
      </button>
    </div>
  );
};

export default function DataTable({ 
  data, 
  tableName, 
  onDataUpdate, 
  currentPage, 
  totalPages, 
  totalRecords, 
  onPageChange,
  isAdmin,
  onDeleteRecord
}) {
  const [editingRow, setEditingRow] = useState(null);
  const [editedData, setEditedData] = useState({});
  const [originalData, setOriginalData] = useState({});

  const handleEditClick = (row) => {
    if (!isAdmin) {
      alert('Only admins can edit records');
      return;
    }
    setEditingRow(row.id);
    setEditedData(row);
    setOriginalData(row);
  };

  const handleSaveClick = async (rowId) => {
    const changeRequestPayload = {
      table_name: tableName,
      record_id: rowId,
      old_values: originalData,
      new_values: editedData,
    };

    try {
      await axios.post(`${API_URL}/changes`, changeRequestPayload);
      onDataUpdate(editedData);
      setEditingRow(null);
      alert('Change request submitted for approval');
    } catch (err) {
      console.error("Failed to save the change:", err);
      alert("Error: Could not save changes. Check the console for details.");
    }
  };

  const handleCancelClick = () => {
    setEditingRow(null);
    setEditedData({});
    setOriginalData({});
  };

  const handleInputChange = (e, field) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setEditedData({ ...editedData, [field]: value });
  };

  const renderCellContent = (value, fieldName) => {
    // Check if the value is JSON
    if (typeof value === 'object' && value !== null) {
      return <JsonViewer data={value} label={`{${Object.keys(value).length} items}`} />;
    }
    
    if (typeof value === 'string') {
      try {
        const parsed = JSON.parse(value);
        if (typeof parsed === 'object') {
          return <JsonViewer data={parsed} label={`{${Object.keys(parsed).length} items}`} />;
        }
      } catch {
        // Not JSON, continue with normal rendering
      }
    }
    
    // For editing mode, show input field
    if (editingRow && fieldName !== 'id') {
      return (
        <input
          type="text"
          className="input-field"
          value={editedData[fieldName] || ''}
          onChange={(e) => handleInputChange(e, fieldName)}
        />
      );
    }
    
    // Normal display
    return String(value || '');
  };
  
  if (!data || data.length === 0) {
    return (
      <div className="table-container">
        <h2 className="table-header">{tableName}</h2>
        <p className="info-message">No data to display in this table.</p>
      </div>
    );
  }

  const headers = Object.keys(data[0]);

  return (
    <div className="table-container">
      <h2 className="table-header">{tableName}</h2>
      <table className="styled-table">
        <thead>
          <tr>
            {headers.map(header => (
                <th key={header}>
                    <div className="header-content">
                        {header}
                        <SortIcon />
                    </div>
                </th>
            ))}
            {isAdmin && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.id}>
              {headers.map(header => (
                <td key={header}>
                  {renderCellContent(row[header], header)}
                </td>
              ))}
              {isAdmin && (
                <td className="actions-cell">
                  {editingRow === row.id ? (
                    <div className="edit-actions">
                      <button onClick={() => handleSaveClick(row.id)} className="action-button save-button">
                        Save
                      </button>
                      <button onClick={handleCancelClick} className="action-button cancel-button">
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="edit-actions">
                      <button onClick={() => handleEditClick(row)} className="link-button">
                        Edit
                      </button>
                      <button onClick={() => onDeleteRecord(row.id)} className="link-button delete-button">
                        Delete
                      </button>
                    </div>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-footer">
        <Pagination 
          currentPage={currentPage}
          totalPages={totalPages}
          totalRecords={totalRecords}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
}
