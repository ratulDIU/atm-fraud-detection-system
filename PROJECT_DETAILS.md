# ATM Fraud Detection System - Complete Project Details

## 📋 Project Overview

**SecureATM** is a real-time fraud detection system for ATM withdrawals that analyzes transaction patterns using advanced algorithms to identify suspicious behavior and protect accounts from fraudulent activities.

**Technology Stack:**
- **Backend:** Python, FastAPI, SQLite
- **Frontend:** HTML5, TailwindCSS, Vanilla JavaScript
- **Database:** SQLite with 3 main tables
- **Authentication:** Session-based (localStorage)

---

## 🏗️ Project Structure

```
atm-fraud-detection-system/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── routes.py                  # API routes
│   ├── fraud_service.py           # Core fraud detection logic
│   ├── database/
│   │   ├── db.py                  # Database operations (CRUD)
│   │   ├── schema.sql             # Database schema
│   │   └── atm.db                 # SQLite database file
│   ├── compiler/                  # Legacy C compiler files (not used)
│   ├── input/                     # Input files
│   └── venv/                      # Python virtual environment
│
├── frontend/
│   ├── login.html                 # Login & Register page
│   ├── index.html                 # Main analysis form
│   ├── result.html                # Fraud analysis results page
│   ├── js/
│   │   └── app.js                 # Dynamic transaction handling & API calls
│   ├── css/
│   │   └── style.css              # Custom styles
│   └── tailwind.config.js         # Tailwind configuration
│
├── docs/                          # Documentation
├── .git/                          # Git repository
├── .gitignore                     # Git ignore rules
└── README.md/                     # Project README
```

---

## 🗄️ Database Schema

### 1. **accounts** table
Stores account information and blocking status.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| account_number | INTEGER | Unique account identifier |
| status | TEXT | `ACTIVE`, `TEMP_BLOCK`, or `PERM_BLOCK` |
| blocked_until | TEXT | ISO timestamp for temporary block expiry |

```sql
CREATE TABLE accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number INTEGER UNIQUE,
    status TEXT DEFAULT 'ACTIVE',
    blocked_until TEXT
);
```

### 2. **transactions** table
Records all analyzed transactions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| account | INTEGER | Account number (foreign key) |
| amount | INTEGER | Withdrawal amount in Taka (৳) |
| location | TEXT | GPS coordinates (lat, lng) |
| timestamp | TEXT | ISO timestamp |

```sql
CREATE TABLE transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account INTEGER,
    amount INTEGER,
    location TEXT,
    timestamp TEXT
);
```

### 3. **fraud_reports** table
Stores fraud analysis results.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| account | INTEGER | Account number |
| risk_score | INTEGER | Calculated risk score (0-15+) |
| risk_level | TEXT | `LOW`, `MEDIUM`, or `HIGH` |
| action | TEXT | `WARNING`, `TEMPORARY BLOCK`, `PERMANENT BLOCK` |
| created_at | TEXT | Analysis timestamp |

```sql
CREATE TABLE fraud_reports(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account INTEGER,
    risk_score INTEGER,
    risk_level TEXT,
    action TEXT,
    created_at TEXT
);
```

---

## 🔌 Backend API

### **Backend Files**

#### **main.py** (FastAPI Server)
- Initializes FastAPI application
- Adds CORS middleware for frontend communication
- Includes all routes from `routes.py`
- Calls `init_db()` on startup to initialize database

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from database.db import init_db

app = FastAPI(title="ATM Fraud Detection API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
app.include_router(router)

@app.on_event("startup")
def startup_event():
    init_db()
```

#### **routes.py** (API Endpoints)
Single POST endpoint for fraud analysis.

```
POST /analyze
```

**Request Body:**
```json
{
    "account": "12345",
    "transactions": [
        {
            "amount": "35000",
            "location": "23.8103, 90.4125"
        },
        {
            "amount": "25000",
            "location": "23.7850, 90.3670"
        }
    ],
    "time_interval": 10
}
```

**Response:**
```json
{
    "account": 12345,
    "withdraw_count": 2,
    "total_amount": 60000,
    "risk_score": 7,
    "risk_level": "HIGH",
    "action": "PERMANENT BLOCK",
    "status": "PERM_BLOCK",
    "blocked_until": null,
    "reasons": [
        "Two withdrawals in one session.",
        "Combined withdrawals exceed normal threshold.",
        "Withdrawals occurred at multiple different locations."
    ]
}
```

#### **fraud_service.py** (Fraud Detection Logic)

**Core Functions:**

1. **calculate_risk(transactions, time_interval)**
   - Evaluates risk based on transaction patterns
   - Returns: risk_score, withdraw_count, total_amount, reasons

2. **risk_level(score)**
   - Maps score to risk level
   - LOW (0-2) → MEDIUM (3-5) → HIGH (6+)

3. **punishment(level)**
   - Maps risk level to action
   - WARNING → TEMPORARY BLOCK → PERMANENT BLOCK

4. **analyze_transaction(data)**
   - Main orchestration function
   - Checks account status
   - Calculates risk
   - Updates database
   - Returns analysis result

**Risk Scoring Rules:**

| Scenario | Points | Reason |
|----------|--------|--------|
| Single withdrawal | +0 base | Evaluated separately |
| Single withdrawal 30k-50k | +2 | High amount |
| Single withdrawal >50k | +4 | Large amount |
| 2 withdrawals | +2 base | Multiple in session |
| 2 withdrawals >60k total | +3 | Exceed threshold |
| 3+ withdrawals | +3 base | Multiple withdrawals |
| 3+ withdrawals >70k | +3 | High total |
| Total >100k | +3 | Unusually high |
| Avg amount >30k | +1 | High average |
| Different locations | +3 | Location change |
| Time ≤5 min (2+ txn) | +3 | Quick succession |
| Time 6-15 min (2+ txn) | +1 | Closely spaced |

**Account States:**

- **ACTIVE**: Normal operation
- **TEMP_BLOCK**: 24-hour automatic block (expires after 24 hours)
- **PERM_BLOCK**: Permanent block (no expiry)

#### **database/db.py** (Database Operations)

**Key Functions:**

1. `init_db()` - Create tables if not exist
2. `get_connection()` - SQLite connection
3. `get_account(account_number)` - Retrieve account
4. `create_account(account_number)` - New account
5. `update_account_status(account_number, status, blocked_until)` - Update status
6. `add_transactions(account_number, transactions)` - Store transactions
7. `add_fraud_report(account_number, risk_score, level, action)` - Store report

---

## 🎨 Frontend Details

### **Frontend Files**

#### **login.html** (Authentication)

**Features:**
- Dual form: Login & Register toggle
- Simple session-based authentication
- Username stored in localStorage
- Dummy validation (no backend authentication)
- Professional UI with icons

**User Flow:**
1. User enters username & password
2. Click "Register" or "Sign In"
3. Username stored in `localStorage.user`
4. Redirects to main page

#### **index.html** (Main Analysis Page)

**Components:**

1. **Header**
   - Logo and branding
   - User welcome message
   - Logout button

2. **Account Number Section**
   - Input for account number
   - Required field

3. **Dynamic Transactions Section**
   - Starts with 1 transaction field
   - "Add Another Withdrawal" button to add more (max 10)
   - Each transaction has:
     - Amount input (required if present)
     - Location field (readonly)
     - "Detect" button for GPS (only activates on click)
     - Color-coded sections (green, yellow, blue, purple, pink, orange)
   - "Remove" button appears after first transaction

4. **Time Interval Section**
   - Input for minutes between withdrawals
   - Required field

5. **Error Message Display**
   - Shows validation errors
   - Auto-hides after 5 seconds

6. **Info Cards**
   - Real-time Analysis
   - Location Detection
   - Secure & Private

#### **result.html** (Fraud Analysis Results)

**Components:**

1. **Status Display**
   - Risk level badge (LOW, MEDIUM, HIGH)
   - Current account status
   - Color-coded styling

2. **Metrics Grid**
   - Withdrawal count
   - Total amount
   - Risk score
   - Action taken

3. **Risk Analysis Section**
   - Displays all risk reasons from backend
   - Checkmark bullets for each reason

4. **Block Information**
   - Shows block expiration time if applicable
   - Only displays for TEMP_BLOCK or PERM_BLOCK

5. **Recommendations**
   - 4-step action guide for bank branch
   - Numbered steps for clarity

#### **js/app.js** (Dynamic Functionality)

**Key Features:**

1. **Dynamic Transaction Management**
   ```javascript
   - createTransactionElement(index) - Create colored transaction block
   - addTransactionBtn - Add/remove transactions
   - Color rotation: green → yellow → blue → purple → pink → orange
   ```

2. **Geolocation Detection**
   ```javascript
   - detectLocation(index) - Only on button click
   - Uses Geolocation API (HTML5)
   - Shows accuracy indicator
   - Error handling for permission denied, timeout, etc.
   - Status messages: detecting → success/error
   ```

3. **Form Submission**
   ```javascript
   - Collects all valid transactions
   - Validates: amount > 0 and location filled
   - Sends POST request to http://localhost:8000/analyze
   - Stores result in localStorage
   - Redirects to result.html
   ```

4. **Session Management**
   ```javascript
   - Checks if user logged in
   - Logout clears localStorage and redirects
   ```

#### **css/style.css** (Custom Styles)
- Additional styling beyond Tailwind
- Animations and transitions
- Custom color schemes

---

## 🔄 Complete User Flow

### **Step 1: Authentication**
```
User Opens App
    ↓
Check localStorage for 'user'
    ↓
If not found → Redirect to login.html
    ↓
User Registers/Logs In
    ↓
Username saved to localStorage
    ↓
Redirect to index.html
```

### **Step 2: Transaction Entry**
```
Main Page Loads
    ↓
Show 1 transaction field
    ↓
User enters:
  - Account number
  - First withdrawal amount
  - Click "Detect" for GPS location (ONLY on click, not on page load)
    ↓
User clicks "Add Another Withdrawal" (optional)
    ↓
More transaction fields appear (color-coded)
    ↓
Repeat location detection for each
    ↓
Enter time interval
    ↓
Click "Analyze & Detect Fraud"
```

### **Step 3: Backend Processing**
```
POST /analyze received
    ↓
Check if account exists
  - If not → Create new account
    ↓
Check account status
  - If PERM_BLOCK → Return blocked response
  - If TEMP_BLOCK and not expired → Return blocked response
  - If TEMP_BLOCK and expired → Set to ACTIVE
    ↓
Calculate risk score
  - Evaluate transaction count
  - Check amounts and thresholds
  - Detect location changes
  - Check time intervals
    ↓
Determine risk level: LOW/MEDIUM/HIGH
    ↓
Determine action: WARNING/TEMPORARY BLOCK/PERMANENT BLOCK
    ↓
Update account status in database
    ↓
Store transactions in database
    ↓
Store fraud report in database
    ↓
Return result with details and reasons
```

### **Step 4: Result Display**
```
Frontend receives result
    ↓
Save to localStorage
    ↓
Redirect to result.html
    ↓
Display:
  - Risk level and score
  - Account status
  - All transactions summary
  - Risk reasons
  - Block expiration (if applicable)
  - Bank branch action recommendations
    ↓
User can:
  - View details
  - Click "New Analysis" to go back
  - Logout
```

---

## 🚀 How to Run

### **1. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn
```

### **2. Start Backend Server**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Server runs on:** `http://localhost:8000`

### **3. Open Frontend**
```bash
# Simply open in browser:
file:///path/to/frontend/login.html
```

Or use a local server:
```bash
cd frontend
python -m http.server 8080
# Open http://localhost:8080/login.html
```

---

## 📊 Example Scenarios

### **Scenario 1: Safe Transaction (LOW Risk)**
```
Input:
- Account: 12345
- 1 withdrawal: 15,000 ৳ at Dhaka
- Time interval: -

Analysis:
- Transaction count: 1
- Amount: <30,000
- Result: Risk Score = 0 → LOW → WARNING
- Action: No block, account stays ACTIVE
```

### **Scenario 2: Suspicious Pattern (HIGH Risk)**
```
Input:
- Account: 67890
- 2 withdrawals: 45,000 ৳ (Dhaka) + 35,000 ৳ (Chattogram)
- Time interval: 3 minutes

Analysis:
- Transaction count: 2 (+2 points)
- Total amount: 80,000 ৳ (>60k) (+3 points)
- Different locations (+3 points)
- Quick succession 3 min (≤5 min) (+3 points)
- Total: 11 points → HIGH → PERMANENT BLOCK
- Account Status: PERM_BLOCK
```

### **Scenario 3: Medium Risk (TEMP Block)**
```
Input:
- Account: 54321
- 3 withdrawals: 20k + 20k + 20k = 60,000 ৳ same location
- Time interval: 30 min

Analysis:
- Transaction count: 3 (+3 points)
- Total amount: 60k (45k-70k range) (+2 points)
- Single location (+0 points)
- Time interval >15 min (+0 points)
- Total: 5 points → MEDIUM → TEMPORARY BLOCK
- Account Status: TEMP_BLOCK
- Blocked until: 24 hours later (auto-expires)
```

---

## 🔐 Security Features

1. **Session Management**
   - User session stored in localStorage
   - Logout clears session
   - Automatic redirect if not logged in

2. **Account Protection**
   - Permanent blocks for high-risk accounts
   - Temporary 24-hour blocks for suspicious patterns
   - Automatic block expiration

3. **Data Storage**
   - Transaction history in database
   - Fraud reports logged for audit
   - GPS coordinates stored for location analysis

4. **Location Privacy**
   - GPS only requested on explicit "Detect" click
   - Not required on page load
   - Optional for system access

---

## 📝 Key Technologies

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Fast, modern web framework for backend |
| **SQLite** | Lightweight database for data storage |
| **TailwindCSS** | Utility-first CSS framework for UI |
| **Geolocation API** | Browser's native GPS location service |
| **CORS Middleware** | Enable cross-origin requests |
| **Vanilla JavaScript** | No framework dependencies |
| **HTML5** | Semantic markup and structure |

---

## 📈 Fraud Detection Scoring System

**Total Possible Score:** 0-15+

**Risk Thresholds:**
- **0-2 points**: LOW Risk → WARNING
- **3-5 points**: MEDIUM Risk → TEMPORARY BLOCK (24 hours)
- **6+ points**: HIGH Risk → PERMANENT BLOCK

**Scoring Factors:**
1. **Transaction Count** - Single vs. multiple
2. **Amounts** - Total and averages
3. **Location Changes** - Different coordinates
4. **Time Intervals** - Quick successions
5. **Session Totals** - Very high amounts

---

## 🎯 Future Enhancements

1. Real backend authentication with password hashing
2. Historical behavior analysis
3. Machine learning for pattern recognition
4. Email notifications on blocks
5. Admin dashboard for monitoring
6. Multi-language support
7. 2FA (Two-Factor Authentication)
8. Card details verification
9. Device fingerprinting
10. Real-time alerts to bank staff

---

## ✨ Current Features

✅ Real-time fraud detection
✅ GPS-based location tracking
✅ Dynamic transaction entry (1-10 withdrawals)
✅ Professional UI/UX
✅ Account status tracking
✅ Temporary & permanent blocks
✅ Auto-expiring blocks (24 hours)
✅ Detailed fraud analysis reasons
✅ Session-based authentication
✅ Responsive design
✅ Error handling
✅ Database persistence

---

## 📞 Contact & Support

For questions or issues, check the database or review logs in:
- Backend logs: Terminal output
- Database: `backend/database/atm.db`
- Frontend errors: Browser console (F12)

---

**Project Status:** ✅ Complete and Ready for Deployment

**Version:** 1.0.0
**Last Updated:** April 17, 2026
