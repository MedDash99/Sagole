// frontend/src/ChangeRequests.jsx
import React, { useState, useEffect, useMemo } from 'react';
import apiClient from './api';
import { useAppContext } from './contexts/AppContext';

// --- Helper Function for Comparison ---
/**
 * Compares an original and pending data row to find differences.
 */
const getDiff = (originalRow, pendingRow) => {
  if (!originalRow && pendingRow) {
    return { type: 'added', changes: pendingRow, hasChanges: true };
  }
  if (originalRow && !pendingRow) {
    return { type: 'deleted', changes: originalRow, hasChanges: true };
  }
  if (!originalRow && !pendingRow) {
    return { type: 'none', changes: {}, hasChanges: false };
  }

  const diff = {};
  let hasChanges = false;
  
  // Use pendingRow keys as the source of truth for fields to display
  const allKeys = Object.keys(pendingRow);

  allKeys.forEach(key => {
    // Check against originalRow, which might not have the key if it's new
    if (!originalRow || originalRow[key] !== pendingRow[key]) {
      diff[key] = {
        original: originalRow ? originalRow[key] : undefined,
        pending: pendingRow[key],
        changed: true,
      };
      hasChanges = true;
    } else {
      diff[key] = {
        original: originalRow[key],
        pending: pendingRow[key],
        changed: false,
      };
    }
  });

  // Determine type based on changes
  const type = !originalRow ? 'added' : hasChanges ? 'modified' : 'unchanged';
  return { type, changes: diff, hasChanges };
};

export default function ChangeRequests() {
    const { currentEnvironment } = useAppContext();
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchRequests = async () => {
            try {
                setLoading(true);
                const response = await apiClient.get(`/${currentEnvironment}/changes`);
                // The backend returns { changes: [{ change_details, original_record }] }
                setRequests(response.data.changes || []);
            } catch (err) {
                setError('Failed to fetch change requests.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchRequests();
    }, [currentEnvironment]);
    
    const handleAction = async (id, action) => {
        try {
            await apiClient.post(`/${currentEnvironment}/changes/${id}/${action}`);
            setRequests(prev => prev.filter(req => req.change_details.id !== id));
            alert(`Change request ${action}ed successfully`);
        } catch (err) {
            console.error(`Failed to ${action} change request:`, err);
            alert(`Failed to ${action} change request. Please try again.`);
        }
    };
    
    if (loading) return <p className="text-center p-4">Loading change requests...</p>;
    if (error) return <p className="text-center p-4 text-red-500">{error}</p>;

    return (
        <div className="p-4 sm:p-6 lg:p-8">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Admin Change Review</h1>
                <p className="mt-2 text-lg text-slate-600">Review, approve, or reject pending changes submitted by users.</p>
            </header>

            {requests.length === 0 ? (
                <div className="text-center p-8 bg-white rounded-lg shadow border border-slate-200">
                    <h3 className="text-xl font-bold text-slate-800">All Clear!</h3>
                    <p className="text-slate-600 mt-2">There are no pending changes to review.</p>
                </div>
            ) : (
                <div className="space-y-8">
                    {requests.map(({ change_details, original_record }) => (
                        <ChangeRequestCard 
                            key={change_details.id}
                            changeDetails={change_details}
                            originalRecord={original_record}
                            onAction={handleAction}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

// --- Component for a single Change Request Card ---
function ChangeRequestCard({ changeDetails, originalRecord, onAction }) {
    
    const { type, changes } = useMemo(() => {
        const pendingRecord = { ...originalRecord, ...changeDetails.new_values };
        if (!originalRecord) {
             return getDiff(null, pendingRecord);
        }
        return getDiff(originalRecord, pendingRecord);
    }, [originalRecord, changeDetails.new_values]);

    const isNew = type === 'added';
    const allKeys = Object.keys(changes);

    const addedCellStyle = 'bg-green-100 text-green-800';
    const deletedCellStyle = 'bg-red-100 text-red-800';
    
    return (
        <div className="bg-white p-6 rounded-lg shadow-md border border-slate-200">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h2 className="text-xl font-bold text-slate-800">
                        Change Request for: <span className="font-mono bg-slate-100 px-2 py-1 rounded-md text-slate-600">{changeDetails.table_name}</span>
                    </h2>
                    <p className="text-sm text-slate-500 mt-1">
                        By: <span className="font-medium">{changeDetails.submitted_by}</span> on {new Date(changeDetails.submitted_at).toLocaleString()}
                    </p>
                </div>
                <div className="flex space-x-2">
                    <button 
                        className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        onClick={() => onAction(changeDetails.id, 'reject')}
                    >
                        Reject
                    </button>
                    <button 
                        className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                        onClick={() => onAction(changeDetails.id, 'approve')}
                    >
                        Approve
                    </button>
                </div>
            </div>

            <div className="flex items-center space-x-4 text-sm text-slate-600 mb-4">
                <div className="flex items-center">
                    <span className="w-3 h-3 rounded-full bg-red-200 border border-red-300 mr-2"></span>
                    <span>Original Values</span>
                </div>
                <div className="flex items-center">
                    <span className="w-3 h-3 rounded-full bg-green-200 border border-green-300 mr-2"></span>
                    <span>Pending Values</span>
                </div>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-lg">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-700 uppercase bg-slate-50">
                        <tr>
                            <th className="p-3 font-semibold text-slate-600">Field</th>
                            <th className="p-3 font-semibold text-slate-600">Original Value</th>
                            <th className="p-3 font-semibold text-slate-600">Pending Value</th>
                        </tr>
                    </thead>
                    <tbody className="text-slate-700">
                        {allKeys.map(key => {
                            const change = changes[key];
                            const originalValue = change?.original?.toString() ?? 'N/A';
                            const pendingValue = change?.pending?.toString() ?? 'N/A';
                            const isChanged = change?.changed || isNew;

                            return (
                                <tr key={key} className="border-b border-slate-200 last:border-b-0">
                                    <td className="p-3 font-mono font-medium text-slate-600 bg-slate-50 w-1/4">{key}</td>
                                    <td className={`p-3 font-mono ${isChanged && !isNew ? deletedCellStyle : ''} w-3/8`}>
                                        {isNew ? <span className="text-slate-400 italic">New Record</span> : originalValue}
                                    </td>
                                    <td className={`p-3 font-mono ${isChanged ? addedCellStyle : ''} w-3/8`}>{pendingValue}</td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
