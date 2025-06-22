import React from 'react';

const styles = {
  tableContainer: {
    marginTop: '20px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    borderBottom: '2px solid #ddd',
    padding: '12px',
    textAlign: 'left',
    backgroundColor: '#f2f2f2',
  },
  td: {
    borderBottom: '1px solid #ddd',
    padding: '12px',
  },
  tr: {
    '&:hover': {
      backgroundColor: '#f5f5f5',
    }
  },
  noData: {
    textAlign: 'center',
    padding: '20px',
    color: '#777',
  }
};

function DataTable({ data, tableName }) {
  if (!data || data.length === 0) {
    return (
        <div style={styles.tableContainer}>
            <h2>{tableName}</h2>
            <p style={styles.noData}>No data to display in this table.</p>
        </div>
    );
  }

  // Get the column headers from the keys of the first object in the data array
  const headers = Object.keys(data[0]);

  return (
    <div style={styles.tableContainer}>
      <h2>{tableName}</h2>
      <table style={styles.table}>
        <thead>
          <tr>
            {headers.map(header => (
              <th key={header} style={styles.th}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} style={styles.tr}>
              {headers.map(header => (
                <td key={header} style={styles.td}>
                  {/* Convert boolean values to strings for display */}
                  {typeof row[header] === 'boolean' ? String(row[header]) : row[header]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
