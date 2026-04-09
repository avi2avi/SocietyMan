from datetime import date, timedelta


def predict_next_service(last_service_date: date, interval_days: int) -> date:
    return last_service_date + timedelta(days=interval_days)


def upcoming_alerts(asset_maintenance_data: list[dict]) -> list[dict]:
    alerts = []
    today = date.today()
    for row in asset_maintenance_data:
        due_date = predict_next_service(row["last_service_date"], row["interval_days"])
        if (due_date - today).days <= 14:
            alerts.append({"asset": row["asset"], "due_date": due_date.isoformat()})
    return alerts
