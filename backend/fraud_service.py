from datetime import datetime, timedelta

from database.db import (
    add_fraud_report,
    add_transactions,
    create_account,
    get_account,
    update_account_status,
)

BLOCK_DURATION_HOURS = 24
ACTIVE_STATUS = "ACTIVE"
TEMP_BLOCK_STATUS = "TEMP_BLOCK"
PERM_BLOCK_STATUS = "PERM_BLOCK"


def parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def calculate_risk(transactions, time_interval):
    withdraw_count = len(transactions)
    total_amount = sum(parse_int(t["amount"]) for t in transactions)
    locations = [str(t.get("location", "")).strip().lower() for t in transactions if t.get("location")]
    unique_locations = len(set(locations))
    location_change = unique_locations > 1

    risk_score = 0
    reasons = []

    if withdraw_count == 1:
        reasons.append("Single transaction submitted.")
        if total_amount > 50000:
            risk_score += 4
            reasons.append("Large single withdrawal amount.")
        elif total_amount > 30000:
            risk_score += 2
            reasons.append("High single withdrawal amount.")
    elif withdraw_count == 2:
        risk_score += 2
        reasons.append("Two withdrawals in one session.")
        if total_amount > 60000:
            risk_score += 3
            reasons.append("Combined withdrawals exceed normal threshold.")
        elif total_amount > 35000:
            risk_score += 1
            reasons.append("Moderate withdrawal total for two transactions.")
    else:
        risk_score += 3
        reasons.append("Multiple withdrawals in one session.")
        if total_amount > 70000:
            risk_score += 3
            reasons.append("High overall withdrawal value.")
        elif total_amount > 45000:
            risk_score += 2
            reasons.append("Significant total withdrawal amount.")

    if total_amount > 100000:
        risk_score += 3
        reasons.append("Transaction value is unusually high for a single session.")

    avg_amount = total_amount / withdraw_count if withdraw_count else 0
    if avg_amount > 30000:
        risk_score += 1
        reasons.append("Average withdrawal amount is higher than expected.")

    if location_change:
        risk_score += 3
        reasons.append("Withdrawals occurred at multiple different locations.")

    if withdraw_count > 1:
        if time_interval is not None:
            if time_interval <= 5:
                risk_score += 3
                reasons.append("Transactions were executed in quick succession.")
            elif time_interval <= 15:
                risk_score += 1
                reasons.append("Transactions were closely spaced in time.")
        else:
            reasons.append("No time interval provided; risk reviewed based on transaction pattern.")
    else:
        reasons.append("Single transaction; timing is not used for risk scoring.")

    return {
        "risk_score": risk_score,
        "withdraw_count": withdraw_count,
        "total_amount": total_amount,
        "location_change": location_change,
        "reasons": reasons,
    }


def risk_level(score):
    if score <= 2:
        return "LOW"
    elif score <= 5:
        return "MEDIUM"
    return "HIGH"


def punishment(level):
    if level == "LOW":
        return "WARNING"
    if level == "MEDIUM":
        return "TEMPORARY BLOCK"
    return "PERMANENT BLOCK"


def is_blocked(account):
    if not account:
        return False

    status = account.get("status")
    blocked_until = account.get("blocked_until")

    if status == PERM_BLOCK_STATUS:
        return True

    if status == TEMP_BLOCK_STATUS and blocked_until:
        try:
            blocked_time = datetime.fromisoformat(blocked_until)
            return datetime.utcnow() < blocked_time
        except ValueError:
            return False

    return False


def analyze_transaction(data):
    account_number = parse_int(data.get("account"))
    transactions = data.get("transactions") or []
    time_interval = parse_int(data.get("time_interval"), default=None)

    if account_number <= 0:
        return {
            "error": "Invalid account number",
            "status": "ERROR",
        }

    account = get_account(account_number)
    if not account:
        account = create_account(account_number)

    if account["status"] == PERM_BLOCK_STATUS:
        return {
            "account": account_number,
            "status": PERM_BLOCK_STATUS,
            "message": "Account permanently blocked. No transactions are allowed.",
            "action": "PERMANENT BLOCK",
        }

    if account["status"] == TEMP_BLOCK_STATUS and account["blocked_until"]:
        try:
            blocked_time = datetime.fromisoformat(account["blocked_until"])
            if datetime.utcnow() < blocked_time:
                return {
                    "account": account_number,
                    "status": TEMP_BLOCK_STATUS,
                    "blocked_until": account["blocked_until"],
                    "message": "Account is temporarily blocked. Please try again later.",
                    "action": "TEMPORARY BLOCK",
                }
            else:
                update_account_status(account_number, ACTIVE_STATUS, None)
                account["status"] = ACTIVE_STATUS
                account["blocked_until"] = None
        except ValueError:
            pass

    transactions = [
        {
            "amount": parse_int(t.get("amount"), default=0),
            "location": str(t.get("location", "")).strip()
        }
        for t in transactions
    ]
    transactions = [t for t in transactions if t["amount"] > 0 and t["location"]]

    if not transactions:
        return {
            "account": account_number,
            "status": account["status"],
            "message": "No valid transactions provided. Please submit at least one amount and location.",
            "action": "WARNING",
        }

    risk_data = calculate_risk(transactions, time_interval)
    risk_score = risk_data["risk_score"]
    level = risk_level(risk_score)
    action = punishment(level)

    blocked_until = None
    status = ACTIVE_STATUS

    if action == "TEMPORARY BLOCK":
        status = TEMP_BLOCK_STATUS
        blocked_until = (datetime.utcnow() + timedelta(hours=BLOCK_DURATION_HOURS)).isoformat()
    elif action == "PERMANENT BLOCK":
        status = PERM_BLOCK_STATUS

    update_account_status(account_number, status, blocked_until)
    add_fraud_report(account_number, risk_score, level, action)
    add_transactions(account_number, transactions)

    return {
        "account": account_number,
        "withdraw_count": len(transactions),
        "total_amount": risk_data["total_amount"],
        "risk_score": risk_score,
        "risk_level": level,
        "action": action,
        "status": status,
        "blocked_until": blocked_until,
        "reasons": risk_data["reasons"],
    }