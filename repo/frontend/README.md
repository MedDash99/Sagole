# Frontend

## Setup

1.  **Install Dependencies:**
    ```bash
    npm install
    ```
2.  **Run the application:**
    ```bash
    npm run dev
    ```

The frontend will be running on `http://localhost:5173` by default and will connect to the backend server running on port 8000.

## Features

- Modern React SPA with Vite for fast development
- Global state management (AppContext)
- Environment selector (dev/test/prod)
- Table browsing, filtering, and pagination
- Admin-only record editing and add-record modal
- Git-style diff viewer for change requests
- Responsive, mobile-friendly design
- Demo login for admin access
- Professional JSON viewer with popover

## Usage

- **Start the app:** `npm run dev`
- **Login:** Click "Demo Login (Admin)" for admin access
- **Browse data:** Select tables, paginate, filter, and view records
- **Edit/add records:** Admins can edit or add records (creates change requests)
- **Approve/reject changes:** Admins review and approve/reject via the Change Requests view
- **Switch environments:** Use the environment dropdown in the header

## Future Enhancements

- Real authentication system
- User management
- Query builder for Predefined Queries
- Advanced settings configuration
- Export functionality
- Real-time notifications
- *Advanced filtering options
- Bulk operations
- Data visualization
