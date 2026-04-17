CREATE TABLE accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number INTEGER UNIQUE,
    status TEXT DEFAULT 'ACTIVE',
    blocked_until TEXT
);

CREATE TABLE transactions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
account INTEGER,
amount INTEGER,
location TEXT,
timestamp TEXT
);

CREATE TABLE fraud_reports(
id INTEGER PRIMARY KEY AUTOINCREMENT,
account INTEGER,
risk_score INTEGER,
risk_level TEXT,
action TEXT,
created_at TEXT
);

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number INTEGER UNIQUE,
    card_holder_name TEXT NOT NULL,
    mobile_number TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_verified INTEGER DEFAULT 0,
    otp_code TEXT,
    otp_expires_at TEXT
);