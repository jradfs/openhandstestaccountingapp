# OpenHands Accounting System

A comprehensive Flask-based accounting and bookkeeping system designed for accounting firms to manage multiple clients.

## Features

- **Client Management**
  - Multiple client support
  - Client profiles and settings
  - Fiscal year tracking

- **Transaction Management**
  - CSV import support
  - AI-powered transaction categorization
  - Batch processing
  - Transaction history

- **Financial Reports**
  - Income Statements
  - Balance Sheets
  - Custom date ranges
  - Excel export

- **Task Management**
  - Task assignment
  - Priority levels
  - Due date tracking
  - Status updates

- **User Management**
  - Role-based access control
  - Staff assignment
  - Activity logging

## Setup

1. Clone the repository:
```bash
git clone https://github.com/jradfs/openhandstestaccountingapp.git
cd openhandstestaccountingapp
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create required directories:
```bash
mkdir -p instance static/uploads
```

5. Generate test data (optional):
```bash
python seed.py
```

6. Run the application:
```bash
python run.py
```

7. Access the application at http://localhost:3000

## Test Users

After running seed.py, you can log in with these credentials:

- **Admin User**
  - Email: admin@example.com
  - Password: admin123

- **Staff Users**
  - Email: staff1@example.com
  - Password: staff1
  - Email: staff2@example.com
  - Password: staff2
  - Email: staff3@example.com
  - Password: staff3

## Transaction Import

The system accepts CSV files with the following columns:
- date: Transaction date (YYYY-MM-DD)
- description: Transaction description
- amount: Transaction amount (negative for expenses)
- category: Transaction category
- account: Account name

A sample CSV file is provided at `static/sample_transactions.csv`.

## Directory Structure

```
openhandstestaccountingapp/
├── instance/               # Database and instance-specific files
├── static/                # Static files (CSS, JS, uploads)
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── uploads/          # Uploaded files
├── templates/            # HTML templates
│   ├── auth/            # Authentication templates
│   ├── dashboard/       # Dashboard templates
│   ├── clients/         # Client management templates
│   ├── transactions/    # Transaction templates
│   ├── reports/         # Report templates
│   └── tasks/           # Task management templates
├── routes/              # Route handlers
├── utils/              # Utility functions
├── models.py           # Database models
├── config.py          # Application configuration
├── seed.py            # Test data generation
└── run.py            # Application entry point
```

## Features by Module

### Client Management
- Client registration
- Business information
- Document management
- Client history

### Transaction Management
- CSV import
- Manual entry
- Batch processing
- Transaction categorization
- Status tracking

### Financial Reports
- Income Statement
- Balance Sheet
- Custom date ranges
- Export to Excel
- Report history

### Task Management
- Task creation
- Assignment
- Priority levels
- Due dates
- Status tracking

### User Management
- User roles
- Access control
- Activity logging
- Staff assignments