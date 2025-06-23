import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const AddRecordModal = ({ isOpen, onClose, tableName, onRecordAdded }) => {
  const [formData, setFormData] = useState({});
  const [tableSchema, setTableSchema] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [schemaLoading, setSchemaLoading] = useState(false);

  // Fetch table schema when modal opens
  useEffect(() => {
    if (isOpen && tableName) {
      fetchTableSchema();
    }
  }, [isOpen, tableName]);

  const fetchTableSchema = async () => {
    try {
      setSchemaLoading(true);
      const response = await axios.get(`${API_URL}/tables/${tableName}/schema`);
      setTableSchema(response.data.schema);
      
      // Initialize form data with empty values for all columns
      const initialData = {};
      response.data.schema.forEach(column => {
        if (!column.primary_key) { // Skip primary key columns
          initialData[column.name] = '';
        }
      });
      setFormData(initialData);
    } catch (err) {
      setError('Failed to fetch table schema');
      console.error('Error fetching schema:', err);
    } finally {
      setSchemaLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const changeRequestPayload = {
        table_name: tableName,
        record_id: null, // New record
        old_values: {},
        new_values: formData,
      };

      await axios.post(`${API_URL}/changes`, changeRequestPayload);
      onRecordAdded();
      onClose();
      setFormData({});
    } catch (err) {
      setError('Failed to create change request. Please try again.');
      console.error('Error creating change request:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderFormField = (column) => {
    if (column.primary_key) {
      return null; // Skip primary key fields
    }

    const fieldType = getFieldType(column.type);
    const fieldName = column.name;

    return (
      <div key={fieldName} className="form-group">
        <label>
          {fieldName}
          {!column.nullable && <span className="required">*</span>}
        </label>
        {fieldType === 'textarea' ? (
          <textarea
            value={formData[fieldName] || ''}
            onChange={(e) => handleInputChange(fieldName, e.target.value)}
            required={!column.nullable}
            rows={3}
          />
        ) : fieldType === 'select' ? (
          <select
            value={formData[fieldName] || ''}
            onChange={(e) => handleInputChange(fieldName, e.target.value)}
            required={!column.nullable}
          >
            <option value="">Select {fieldName}</option>
            <option value="true">True</option>
            <option value="false">False</option>
          </select>
        ) : (
          <input
            type={fieldType}
            value={formData[fieldName] || ''}
            onChange={(e) => handleInputChange(fieldName, e.target.value)}
            required={!column.nullable}
            placeholder={`Enter ${fieldName}`}
          />
        )}
      </div>
    );
  };

  const getFieldType = (sqlType) => {
    const type = sqlType.toLowerCase();
    if (type.includes('text') || type.includes('varchar')) {
      return 'text';
    }
    if (type.includes('int') || type.includes('number')) {
      return 'number';
    }
    if (type.includes('date') || type.includes('timestamp')) {
      return 'datetime-local';
    }
    if (type.includes('bool')) {
      return 'select';
    }
    return 'text';
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Add New Record to {tableName}</h2>
          <button onClick={onClose} className="modal-close">&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="error-message">{error}</div>}
            
            {schemaLoading ? (
              <div className="loading-message">Loading table schema...</div>
            ) : (
              <>
                {tableSchema.length === 0 ? (
                  <div className="info-message">No editable fields found for this table.</div>
                ) : (
                  tableSchema.map(renderFormField)
                )}
              </>
            )}
          </div>
          
          <div className="modal-footer">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={loading || schemaLoading || tableSchema.length === 0}
            >
              {loading ? 'Creating...' : 'Create Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddRecordModal; 