// frontend/src/DataBrowser.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from './contexts/AppContext';
import DataTable from './DataTable';
import AddRecordModal from './components/AddRecordModal';
import FilterModal from './components/FilterModal';

const API_URL = 'http://localhost:8000/api/v1';

export default function DataBrowser() {
  const { currentEnvironment, isAdmin, appState, updateAppState } = useAppContext();
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(appState.selectedTable);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(appState.currentPage);
  const [pageSize] = useState(10);
  const [totalRecords, setTotalRecords] = useState(0);
  const [filters, setFilters] = useState(appState.filters);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);

  // Effect 1: Fetch the list of tables when environment changes or component mounts
  useEffect(() => {
    const controller = new AbortController();
    const fetchTables = async () => {
      try {
        setError(null);
        const response = await axios.get(`${API_URL}/tables`, { 
          signal: controller.signal,
          params: { environment: currentEnvironment }
        });
        setTables(response.data.tables);
        
        // If no table is selected or the selected table doesn't exist in new environment
        if (response.data.tables.length > 0 && (!selectedTable || !response.data.tables.includes(selectedTable))) {
          const newSelectedTable = response.data.tables[0];
          setSelectedTable(newSelectedTable);
        }
      } catch (err) {
        if (err.name !== 'CanceledError') {
          setError('Failed to connect to the backend.');
          console.error(err);
        }
      }
    };
    fetchTables();
    return () => controller.abort();
  }, [currentEnvironment]);

  // Effect 2: Fetch data for the selected table with pagination and filters
  useEffect(() => {
    if (!selectedTable) return;
    const controller = new AbortController();
    const fetchTableData = async () => {
      try {
        setLoading(true);
        setError(null);
        setTableData([]);
        
        const params = {
          page: currentPage,
          page_size: pageSize,
          environment: currentEnvironment
        };

        // Add filters to params
        if (filters.length > 0) {
          params.filters = JSON.stringify(filters);
        }

        const response = await axios.get(`${API_URL}/tables/${selectedTable}`, { 
          signal: controller.signal,
          params
        });
        
        setTableData(response.data.data);
        setTotalRecords(response.data.total || response.data.data.length);
      } catch (err) {
        if (err.name !== 'CanceledError') {
          setError(`Failed to fetch data for table: ${selectedTable}`);
          setTableData([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };
    fetchTableData();
    return () => controller.abort();
  }, [selectedTable, currentPage, filters, currentEnvironment]);

  // Update app state when local state changes
  useEffect(() => {
    updateAppState({
      selectedTable,
      currentPage,
      filters
    });
  }, [selectedTable, currentPage, filters, updateAppState]);

  const handleDataUpdate = (updatedRow) => {
    setTableData(currentData =>
      currentData.map(row => (row.id === updatedRow.id ? updatedRow : row))
    );
  };

  const handleAddRecord = () => {
    setShowAddModal(true);
  };

  const handleRecordAdded = () => {
    // Refresh the table data
    setCurrentPage(1);
    setFilters([]);
  };

  const handleFilter = () => {
    setShowFilterModal(true);
  };

  const handleApplyFilter = (newFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when applying filters
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName);
    setCurrentPage(1);
    setFilters([]);
  };

  const handleDeleteRecord = async (recordId) => {
    try {
      await axios.delete(`${API_URL}/tables/${selectedTable}/${recordId}`);
      setTableData(currentData => currentData.filter(row => row.id !== recordId));
      alert('Record deleted successfully');
    } catch (err) {
      console.error("Failed to delete the record:", err);
      alert("Error: Could not delete the record. Check the console for details.");
    }
  };

  const totalPages = Math.ceil(totalRecords / pageSize);

  return (
    <div className="data-browser-container">
      <div className="data-browser-header">
        <h1 className="h1">Data Browser</h1>
      </div>

      <div className="action-bar">
        {isAdmin && (
          <button 
            className="action-button" 
            onClick={handleAddRecord}
          >
            Add Record
          </button>
        )}
        <button 
          className="action-button" 
          onClick={handleFilter}
        >
          Filter
        </button>
      </div>

      <div className="table-layout-container">
        <div className="table-header-bar">
          <div className="table-header-title">Table</div>
          <div className="table-header-value">{selectedTable}</div>
        </div>
        <div className="data-browser-grid">
          <div className="table-list-container">
            {tables.map(table => (
              <button
                key={table}
                onClick={() => handleTableSelect(table)}
                className={`table-list-item ${selectedTable === table ? 'active' : ''}`}
              >
                {table}
              </button>
            ))}
          </div>
          <div className="data-table-view">
            {error && <p className="error-message">{error}</p>}
            {loading && <div className="table-container"><p className="info-message">Loading...</p></div>}
            {!loading && selectedTable && (
              <DataTable
                data={tableData}
                tableName={selectedTable}
                onDataUpdate={handleDataUpdate}
                onDeleteRecord={handleDeleteRecord}
                currentPage={currentPage}
                totalPages={totalPages}
                totalRecords={totalRecords}
                onPageChange={handlePageChange}
                isAdmin={isAdmin}
              />
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <AddRecordModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        tableName={selectedTable}
        onRecordAdded={handleRecordAdded}
      />

      <FilterModal
        isOpen={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        onApplyFilter={handleApplyFilter}
        columns={tableData.length > 0 ? Object.keys(tableData[0]) : []}
      />
    </div>
  );
}
