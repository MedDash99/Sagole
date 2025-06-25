import React, { useState } from 'react';

const FilterModal = ({ isOpen, onClose, onApplyFilter, columns }) => {
  const [filters, setFilters] = useState([]);

  const addFilter = () => {
    setFilters([...filters, { column: '', operator: '=', value: '' }]);
  };

  const removeFilter = (index) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const updateFilter = (index, field, value) => {
    const newFilters = [...filters];
    newFilters[index] = { ...newFilters[index], [field]: value };
    setFilters(newFilters);
  };

  const handleApply = () => {
    const validFilters = filters.filter(f => f.column && f.value);
    onApplyFilter(validFilters);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Filter Data</h2>
          <button onClick={onClose} className="modal-close">&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="filter-list">
            {filters.map((filter, index) => (
              <div key={index} className="filter-row">
                <select
                  value={filter.column}
                  onChange={(e) => updateFilter(index, 'column', e.target.value)}
                >
                  <option value="">Select Column</option>
                  {columns?.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
                
                <select
                  value={filter.operator}
                  onChange={(e) => updateFilter(index, 'operator', e.target.value)}
                >
                  <option value="=">=</option>
                  <option value="!=">!=</option>
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<=">&lt;=</option>
                  <option value="LIKE">LIKE</option>
                </select>
                
                <input
                  type="text"
                  placeholder="Value"
                  value={filter.value}
                  onChange={(e) => updateFilter(index, 'value', e.target.value)}
                />
                
                <button
                  type="button"
                  onClick={() => removeFilter(index)}
                  className="remove-filter"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          
          <button type="button" onClick={addFilter} className="add-filter-btn">
            + Add Filter
          </button>
        </div>
        
        <div className="modal-footer">
          <button type="button" onClick={onClose} className="add-filter-btn">
            Cancel
          </button>
          <button type="button" onClick={handleApply} className="add-filter-btn">
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
};

export default FilterModal; 