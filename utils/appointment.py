import json

def send_appointment(normalized_data):
    data = normalized_data.get("normalized", {})
    department = data.get("department")
    date = data.get("date")
    time = data.get("time")
    tz = data.get("tz")
    return {
        "appointment": {
            "department": department,
            "date": date,
            "time": time,
            "tz": tz
        },
        "status": "ok"
    }
