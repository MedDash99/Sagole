// frontend/src/ChangeRequests.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DiffViewer from './components/DiffViewer';

const API_URL = 'http://localhost:8000/api/v1';

export default function ChangeRequests() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const controller = new AbortController();
        const fetchRequests = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await axios.get(`${API_URL}/changes`, { signal: controller.signal });
                setRequests(response.data.changes);
            } catch (err) {
                if(err.name !== 'CanceledError') {
                    setError('Failed to fetch change requests.');
                    console.error(err);
                }
            } finally {
                 if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        };

        fetchRequests();
        return () => controller.abort();
    }, []);
    
    const handleApprove = async (id) => {
        try {
            await axios.post(`${API_URL}/changes/${id}/approve`);
            // Remove the approved request from the list
            setRequests(prev => prev.filter(req => req.id !== id));
            alert('Change request approved successfully');
        } catch (err) {
            console.error('Failed to approve change request:', err);
            alert('Failed to approve change request. Please try again.');
        }
    };

    const handleReject = async (id) => {
        try {
            await axios.post(`${API_URL}/changes/${id}/reject`);
            // Remove the rejected request from the list
            setRequests(prev => prev.filter(req => req.id !== id));
            alert('Change request rejected successfully');
        } catch (err) {
            console.error('Failed to reject change request:', err);
            alert('Failed to reject change request. Please try again.');
        }
    };

    if (loading) {
        return <p className="info-message">Loading change requests...</p>
    }
    if (error) {
        return <p className="error-message">{error}</p>
    }

    return (
        <div>
            <h1 className="h1">Pending Change Requests</h1>
            {requests.length === 0 ? (
                <p className="info-message">No pending changes for admin approval.</p>
            ) : (
                requests.map(req => (
                    <div key={req.id} className="change-request-card">
                        <div className="change-header">
                            <h3>Change for table: <strong>{req.table_name}</strong> (Record ID: {req.record_id || 'New Record'})</h3>
                            <div className="change-meta">
                                <span>Status: {req.status}</span>
                                <span>Created: {new Date(req.created_at).toLocaleString()}</span>
                            </div>
                        </div>
                        <div className="diff-container">
                            <DiffViewer 
                                oldValues={req.old_values} 
                                newValues={req.new_values} 
                            />
                        </div>
                        <div className="change-actions">
                            <button 
                                className="action-button reject-button" 
                                onClick={() => handleReject(req.id)}
                            >
                                Reject
                            </button>
                            <button 
                                className="action-button approve-button" 
                                onClick={() => handleApprove(req.id)}
                            >
                                Approve
                            </button>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}
