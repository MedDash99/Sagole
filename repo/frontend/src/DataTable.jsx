import { useState } from 'react';
import apiClient from './api';
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
  onDeleteRecord,
  isAdmin
}) {
  const [editingRow, setEditingRow] = useState(null);
  const [editedData, setEditedData] = useState({});
  const [originalData, setOriginalData] = useState({});

  const handleEditClick = (row) => {
    // Any authenticated user can start an edit
    setEditingRow(row.id);
    setEditedData({ ...row });
    setOriginalData({ ...row });
  };

  const handleSaveClick = async (rowId) => {
    // Calculate the delta
    const old_values_delta = {};
    const new_values_delta = {};
    Object.keys(editedData).forEach(key => {
      if (originalData[key] !== editedData[key]) {
        old_values_delta[key] = originalData[key];
        new_values_delta[key] = editedData[key];
      }
    });

    if (Object.keys(new_values_delta).length === 0) {
      setEditingRow(null); // Nothing changed, just exit edit mode
      return;
    }

    const changeRequestPayload = {
      table_name: tableName,
      record_id: rowId,
      old_values: old_values_delta,
      new_values: new_values_delta,
    };

    console.log('🚀 Submitting change request:', changeRequestPayload);
    console.log('🔍 Payload details:', {
      table_name: typeof changeRequestPayload.table_name,
      record_id: typeof changeRequestPayload.record_id,
      old_values: typeof changeRequestPayload.old_values,
      new_values: typeof changeRequestPayload.new_values,
      old_values_content: changeRequestPayload.old_values,
      new_values_content: changeRequestPayload.new_values
    });

    try {
      const response = await apiClient.post(`/changes`, changeRequestPayload);
      console.log('✅ Change request submitted successfully:', response.data);
      setEditingRow(null);
      alert('Change has been submitted for approval.');
    } catch (err) {
      console.error("❌ Failed to submit change for approval:", err);
      console.error("📋 Error details:", {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        statusText: err.response?.statusText
      });
      alert("Error: Could not submit change. Check the console for details.");
    }
  };

  const handleCancelClick = () => {
    setEditingRow(null);
    setEditedData({});
    setOriginalData({});
  };

  const handleInputChange = (e, field) => {
    const originalValue = originalData[field];
    let value;

    if (e.target.type === 'checkbox') {
      value = e.target.checked;
    } else {
      const inputValue = e.target.value;
      // Attempt to convert back to the original type
      if (typeof originalValue === 'number') {
        // Handle potential empty string for number fields
        value = inputValue === '' ? null : Number(inputValue);
      } else if (typeof originalValue === 'boolean') {
        value = inputValue.toLowerCase() === 'true';
      } else {
        value = inputValue;
      }
    }
    setEditedData({ ...editedData, [field]: value });
  };

  const renderCellContent = (value, fieldName, row) => {
    const isEditing = editingRow === row.id;
    // For editing mode, show input field for the specific row
    if (isEditing && fieldName !== 'id') {
      return (
        <input
          type="text"
          className="input-field"
          value={editedData[fieldName] || ''}
          onChange={(e) => handleInputChange(e, fieldName)}
        />
      );
    }

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
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.id}>
              {headers.map(header => (
                <td key={header}>
                  {renderCellContent(row[header], header, row)}
                </td>
              ))}
              <td className="actions-cell">
                {editingRow === row.id ? (
                  <div className="edit-actions">
                    <button onClick={() => handleSaveClick(row.id)} className="action-button save-button">
                      Submit for Approval
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
                    {isAdmin && (
                      <button onClick={() => onDeleteRecord(row.id)} className="link-button delete-button">
                        Delete
                      </button>
                    )}
                  </div>
                )}
              </td>
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
