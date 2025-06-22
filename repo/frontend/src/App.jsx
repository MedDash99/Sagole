import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

// --- Styling Object ---
const styles = {
  app: { fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', display: 'flex', height: '100vh', backgroundColor: '#f4f7f6' },
  sidebar: { width: '250px', borderRight: '1px solid #e0e0e0', padding: '20px', backgroundColor: '#ffffff' },
  content: { flex: 1, padding: '20px', overflowY: 'auto' },
  h1: { color: '#333' },
  h2: { color: '#555', borderBottom: '1px solid #eee', paddingBottom: '10px' },
  error: { color: '#d32f2f', fontWeight: 'bold', backgroundColor: '#ffebee', padding: '10px', borderRadius: '4px' },
  tableButton: {
    display: 'block', width: '100%', padding: '10px', margin: '5px 0', textAlign: 'left',
    backgroundColor: '#e9ecef', border: '1px solid #dee2e6', borderRadius: '4px', cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  activeTableButton: { backgroundColor: '#007bff', color: 'white', borderColor: '#007bff' },
  tableContainer: { marginTop: '20px', backgroundColor: '#fff', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { borderBottom: '2px solid #dee2e6', padding: '12px', textAlign: 'left', backgroundColor: '#f8f9fa' },
  td: { borderBottom: '1px solid #eff2f5', padding: '12px',  verticalAlign: 'middle', color: '#333'},  trHover: { '&:hover': { backgroundColor: '#f8f9fa' } },
  noData: { textAlign: 'center', padding: '20px', color: '#6c757d' },
  actionButton: {
    padding: '6px 12px', fontSize: '14px', borderRadius: '4px', cursor: 'pointer',
    border: '1px solid transparent',
  },
  editButton: { backgroundColor: '#ffc107', color: '#212529', borderColor: '#ffc107' },
  saveButton: { backgroundColor: '#28a745', color: 'white', borderColor: '#28a745' },
  inputField: { width: '90%', padding: '8px', border: '1px solid #ced4da', borderRadius: '4px' },
};


// --- DataTable Component ---
function DataTable({ data, tableName }) {
  const [editingRow, setEditingRow] = useState(null); // Tracks the ID of the row being edited
  const [editedData, setEditedData] = useState({});   // Holds the new data for the row

  const handleEditClick = (row) => {
    setEditingRow(row.id);
    setEditedData(row);
  };

  const handleSaveClick = (id) => {
    console.log("Saving data for row:", id, "New data:", editedData);
    // In the next step, we will send this data to the backend API
    setEditingRow(null);
  };

  const handleInputChange = (e, field) => {
    setEditedData({ ...editedData, [field]: e.target.value });
  };

  if (!data || data.length === 0) {
    return (
        <div style={styles.tableContainer}>
            <h2 style={styles.h2}>{tableName}</h2>
            <p style={styles.noData}>No data to display in this table.</p>
        </div>
    );
  }

  const headers = Object.keys(data[0]);

  return (
    <div style={styles.tableContainer}>
      <h2 style={styles.h2}>{tableName}</h2>
      <table style={styles.table}>
        <thead>
          <tr>
            {headers.map(header => <th key={header} style={styles.th}>{header}</th>)}
            <th style={styles.th}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.id}>
              {headers.map(header => (
                <td key={header} style={styles.td}>
                  {editingRow === row.id && header !== 'id' ? (
                    <input
                      type="text"
                      value={editedData[header]}
                      onChange={(e) => handleInputChange(e, header)}
                      style={styles.inputField}
                    />
                  ) : (
                    String(row[header])
                  )}
                </td>
              ))}
              <td style={styles.td}>
                {editingRow === row.id ? (
                  <button onClick={() => handleSaveClick(row.id)} style={{...styles.actionButton, ...styles.saveButton}}>Save</button>
                ) : (
                  <button onClick={() => handleEditClick(row)} style={{...styles.actionButton, ...styles.editButton}}>Edit</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


// --- Main App Component ---
function App() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTables = async () => {
      try {
        const response = await axios.get(`${API_URL}/tables`);
        setTables(response.data.tables);
      } catch (err) {
        setError('Failed to connect to the backend.');
        console.error(err);
      }
    };
    fetchTables();
  }, []);

  const handleTableClick = async (tableName) => {
    try {
      setLoading(true);
      setSelectedTable(tableName);
      const response = await axios.get(`${API_URL}/tables/${tableName}`);
      setTableData(response.data.data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch data for table: ${tableName}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.app}>
      <aside style={styles.sidebar}>
        <h2 style={styles.h2}>Tables</h2>
        {tables.map(table => (
          <button
            key={table}
            onClick={() => handleTableClick(table)}
            style={{
              ...styles.tableButton,
              ...(selectedTable === table ? styles.activeTableButton : {})
            }}
            onMouseOver={(e) => { if(selectedTable !== table) e.currentTarget.style.backgroundColor = '#f8f9fa'; }}
            onMouseOut={(e) => { if(selectedTable !== table) e.currentTarget.style.backgroundColor = '#e9ecef'; }}
          >
            {table}
          </button>
        ))}
      </aside>

      <main style={styles.content}>
        <h1 style={styles.h1}>Database Admin Panel</h1>
        {error && <p style={styles.error}>{error}</p>}
        {loading && <p>Loading...</p>}
        
        {!loading && selectedTable && <DataTable data={tableData} tableName={selectedTable} />}
        {!selectedTable && !loading && <p>Select a table from the left to view its data.</p>}
      </main>
    </div>
  );
}

export default App;

