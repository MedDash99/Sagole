### **Full Stack Home Assignment Checklist**

### **Backend Requirements (Python/FastAPI)**

* **Core Technology:**  
  - [x] ~~Use Python for the backend.~~  
  - [x] ~~Use FastAPI (preferred) or Flask framework.~~  
  - [x] ~~Use PostgreSQL as the database.~~  
* **Database & Environments:**  
  * [ ] Simulate multiple environments (e.g., dev, test) using separate schemas or databases.  
  * [ ] Backend logic supports switching between environments (via connection string or schema).  
  * [x] ~~Create a metadata table/DB for pending edits (e.g., change\_requests).~~  
* **RESTful API Endpoints:**  
- [x] **~~Tables:~~**  
      * [x] ~~Endpoint to list all tables in the selected environment.~~  
        * [x] ~~Endpoint to get the schema for a specific table.~~  
      - [x] ~~**Data:**~~  
            * [x] ~~Endpoint to view data from a table.~~  
            * [x] ~~Endpoint to filter data in a table.~~  
      - [x] ~~**Editing & Approval Flow:**~~  
            * [x] ~~Endpoint for record editing (Admin only).~~  
            * [x] ~~Endpoint to submit edits for approval (stores changes in change\_requests).~~  
            * [x] ~~Endpoint for admins to approve/reject changes.~~  
* **Approval Logic:**  
  * [x] ~~On approval, apply the changes to the actual database table using SQL.~~  
  * [x] ~~On approval, save a snapshot of the *entire* affected table (as JSON or in a separate snapshot table).~~

### **Frontend Requirements (React)**

* **Core Technology:**  
  * [x] ~~Use React (TypeScript or JavaScript).~~  
  * [x] ~~UI is minimal and clean.~~  
* **User Interface & Features:**  
  * [x] ~~**Authentication:**~~  
    * [x] ~~Create a basic login screen.~~  
    * [x] ~~Use hardcoded users for admin and regular user.~~  
  * [x] ~~**Main View:**~~  
    * [x] ~~Environment selector dropdown (dev, test, stage, prod).~~  
    * [x] ~~Display a list of tables from the selected environment.~~  
    * [x] ~~Table schema viewer.~~  
  * [x] ~~**Data Interaction:**~~  
    * [x] ~~Display table data in a grid/table format.~~  
    * [x] ~~Implement data filtering on the grid.~~  
    * [x] ~~Implement data sorting on the grid.~~  
  * [x] ~~**Role-Based UI (Admin vs. Regular User):**~~  
    * [x] ~~**Admin Only:**~~  
      * [x] ~~Enable inline editing or an edit form for records.~~  
      * [x] ~~Show a "Submit for Approval" button after edits are made.~~  
      * [x] ~~Create a "Change Request Viewer" or "Pending Approvals" screen.~~  
      * [x] ~~Display a visual "diff" showing *before* vs. *after* values for pending changes.~~  
      * [x] ~~Provide "Approve" and "Reject" buttons for each change request.~~  
  * [x] ~~**User Feedback:**~~  
    * [x] ~~Show toast notifications or other UI feedback for success/failure of actions (e.g., "Change Approved\!").~~

### **Setup & Deliverables**

* **PostgreSQL Setup:**  
  * [x] ~~Set up PostgreSQL with at least two schemas/databases (e.g., dev, test).~~  
  * [x] ~~Each environment has 1-2 tables (e.g., users, products).~~  
  * [x] ~~Pre-fill tables with mock data.~~  
  * [x] ~~Create tables for metadata (users, roles, pending\_changes, snapshots).~~  
  * [x] ~~Provide seed scripts or .sql files to set up the database.~~  
* **Project Repository:**  
  * [x] ~~Create a GitHub repository for the project.~~  
  * [x] ~~Structure the repo with /backend and /frontend folders.~~  
* **Documentation (README.md files):**  
  * [ ] **Root README.md:**  
    * [ ] Overall project description.  
  * [ ] **Backend README.md:**  
    * [ ] Setup instructions (environment variables, how to run).  
    * [ ] Notes on any unimplemented features.  
  * [x] ~~**Frontend README.md:**~~  
    * [x] ~~Setup instructions (how to run).~~  
  * [ ] **General Documentation:**  
    * [ ] Provide login details for admin and user roles.  
    * [ ] List any predefined queries available.

### **Bonus Points**

* [ ] Implement JWT or session-based authentication instead of hardcoded users.  
* [ ] Use a library like react-table or MUI DataGrid for the data grid.  
* [x] ~~Use Docker Compose to orchestrate the entire stack (Postgres, API, Frontend).~~  
* [x] ~~Fully implement the roles and permissions system instead of assuming it.~~  
* [ ] Add a feature to export data to CSV or JSON.  
* [x] ~~Add an environment health check endpoint/indicator.~~