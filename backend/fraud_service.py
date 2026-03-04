def calculate_risk(transactions, time_interval):

    withdraw_count = len(transactions)
    total_amount = sum(t["amount"] for t in transactions)

    locations = [t["location"] for t in transactions]
    location_change = len(set(locations)) > 1

    risk_score = 0

    if withdraw_count >= 3:
        risk_score += 3

    if total_amount > 40000:
        risk_score += 3

    if location_change:
        risk_score += 3

    if time_interval <= 5:
        risk_score += 2

    return risk_score


def risk_level(score):

    if score <= 3:
        return "LOW"

    elif score <= 6:
        return "MEDIUM"

    else:
        return "HIGH"


def punishment(level):

    if level == "LOW":
        return "WARNING"

    elif level == "MEDIUM":
        return "TEMPORARY BLOCK"

    else:
        return "PERMANENT BLOCK"


def analyze_transaction(data):

    account = data["account"]
    transactions = data["transactions"]
    time_interval = data["time_interval"]

    withdraw_count = len(transactions)
    total_amount = sum(t["amount"] for t in transactions)

    locations = [t["location"] for t in transactions]
    location_change = len(set(locations)) > 1

    risk_score = 0

    if withdraw_count >= 3:
        risk_score += 3

    if total_amount > 40000:
        risk_score += 3

    if location_change:
        risk_score += 3

    if time_interval <= 5:
        risk_score += 2

    if risk_score <= 3:
        level = "LOW"
        action = "WARNING"

    elif risk_score <= 6:
        level = "MEDIUM"
        action = "TEMPORARY BLOCK"

    else:
        level = "HIGH"
        action = "PERMANENT BLOCK"

    return {
        "account": account,
        "withdraw_count": withdraw_count,
        "total_amount": total_amount,
        "risk_score": risk_score,
        "risk_level": level,
        "action": action
    }