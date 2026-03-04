CREATE TABLE accounts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
account_number INTEGER,
status TEXT
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