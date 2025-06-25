# Database Snapshot Functionality

## Overview

The snapshot functionality is a critical part of the auditing and change-tracking system for the database administration web application. It creates permanent, immutable, point-in-time records of entire database tables when changes are approved.

## Core Concept

The primary goal of the snapshot is to create a complete copy of a database table at the exact moment a change is approved. This is **NOT** a log of what single row changed; it is a **full copy** of the entire table, frozen at the moment a change was made.

### Key Distinctions

- **Live Table** (e.g., `dev.users`): This is mutable and always changing with every new approved edit. It represents the present.
- **Snapshot**: This is immutable and permanent. It represents a moment in the past. Think of it like a git commit—a permanent record of a specific state.

## Purpose

The snapshot functionality provides:

1. **Complete Audit Trail**: See the exact state of the data when a change was made
2. **Data Recovery/Rollback Capability**: Restore the table to a previous state if an approved change causes problems
3. **Historical Analysis**: Compare different states of the data over time
4. **Compliance**: Meet regulatory requirements for data change tracking

## Implementation Details

### Database Schema

The snapshots are stored in a dedicated table:

```sql
CREATE TABLE dev.snapshots (
    id SERIAL PRIMARY KEY,
    change_request_id INTEGER NOT NULL,  -- References pending_changes.id
    table_name VARCHAR(100) NOT NULL,
    snapshot_data JSONB NOT NULL,        -- Complete table data as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Sequence of Operations

When an administrator approves a pending change, the system follows this critical sequence:

1. **Apply the Change**: Execute the SQL query from the pending_changes record to update the live table
2. **Take the Snapshot**: Immediately after the update succeeds, read the entire contents of the affected table (`SELECT * FROM ...`)
3. **Save the Snapshot**: Store this complete copy of the table's data in the snapshots table

### Code Structure

#### Models (`app/models.py`)

The `Snapshot` model has been updated to support full table snapshots:

```python
class Snapshot(Base):
    __tablename__ = "snapshots"
    __table_args__ = {'schema': 'dev'}

    id = Column(Integer, primary_key=True, index=True)
    change_request_id = Column(Integer, nullable=False)  # References pending_changes.id
    table_name = Column(String(100), nullable=False)
    snapshot_data = Column(JSON, nullable=False)  # Complete table data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### Core Functions (`app/db_manager.py`)

##### `approve_change()`
Updated to include snapshot creation as Step 2 in the approval process:

```python
def approve_change(db: Session, change_id: int, admin_user_id: int):
    # Step 1: Apply the change to the target table
    _apply_change_to_table(db, change)
    
    # Step 2: Take a snapshot of the entire table after the change
    _create_table_snapshot(db, change.table_name, change.id)
    
    # Step 3: Create an audit log entry
    # Step 4: Update the change status to approved
```

##### `_create_table_snapshot()`
Creates a complete snapshot of the table:

```python
def _create_table_snapshot(db: Session, table_name: str, change_request_id: int):
    # Get all data from the table (entire table snapshot)
    table_data = get_table_data(table_name=table_name, limit=10000, offset=0)
    
    # Serialize the data to ensure it's JSON compatible
    serialized_data = [_make_record_serializable(record) for record in table_data if record is not None]
    
    # Create the snapshot record
    snapshot = models.Snapshot(
        change_request_id=change_request_id,
        table_name=table_name,
        snapshot_data=serialized_data
    )
    
    db.add(snapshot)
```

#### API Endpoints (`app/api.py`)

New endpoints for accessing snapshot data:

- `GET /api/v1/tables/{table_name}/snapshots` - List all snapshots for a table
- `GET /api/v1/snapshots/{snapshot_id}` - Get full data for a specific snapshot

## Usage Examples

### Creating a Snapshot (Automatic)

Snapshots are created automatically when changes are approved:

1. User submits a change request
2. Admin approves the change via `POST /api/v1/changes/{change_id}/approve`
3. System automatically creates snapshot after applying the change

### Viewing Snapshots

```bash
# List all snapshots for the users table
curl -X GET "http://localhost:8000/api/v1/tables/users/snapshots"

# Get full data for snapshot ID 5
curl -X GET "http://localhost:8000/api/v1/snapshots/5"
```

### Example Response

```json
{
  "table": "users",
  "snapshots": [
    {
      "id": 5,
      "change_request_id": 12,
      "table_name": "users",
      "created_at": "2024-01-15T14:30:00Z",
      "record_count": 247
    },
    {
      "id": 4,
      "change_request_id": 8,
      "table_name": "users", 
      "created_at": "2024-01-14T09:15:00Z",
      "record_count": 246
    }
  ]
}
```

## Data Recovery Process

To restore data from a snapshot:

1. Retrieve the snapshot data: `GET /api/v1/snapshots/{snapshot_id}`
2. Use the `snapshot_data` array to recreate the table state
3. Each record in the array represents a complete row as it existed at that moment

## Performance Considerations

- **Storage**: Each snapshot stores the complete table data, so storage usage scales with table size × number of changes
- **Creation Time**: Snapshot creation time depends on table size (larger tables take longer)
- **Limit**: Current implementation has a 10,000 record limit per snapshot
- **JSON Storage**: Using JSONB in PostgreSQL provides efficient storage and querying

## Testing

Use the provided test script to verify functionality:

```bash
cd repo/backend
python test_snapshot_functionality.py
```

This script:
1. Logs in as admin
2. Checks for pending changes
3. Approves a change
4. Verifies that a snapshot was created
5. Retrieves and validates the snapshot data

## Security Considerations

- Only administrators can approve changes (and thus trigger snapshots)
- Snapshot data is read-only once created
- Access to snapshot endpoints should be restricted to authorized users
- Sensitive data in snapshots follows the same access controls as the live tables

## Future Enhancements

Possible improvements to consider:

1. **Compression**: Implement data compression for large snapshots
2. **Incremental Snapshots**: Store only changes between snapshots
3. **Retention Policies**: Automatic cleanup of old snapshots
4. **Backup Integration**: Integrate with database backup systems
5. **Restoration Tools**: Build UI tools for easy data restoration from snapshots 