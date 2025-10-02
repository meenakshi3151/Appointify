import json

def send_appointment(normalized_data):
    # function is responsible for sending appointment details
    department = normalized_data["department"]
    date = normalized_data["date"]
    time = normalized_data["time"]
    tz = normalized_data.get("tz", "Asia/Kolkata")
    return {
        "appointment": {
            "department": department,
            "date": date,
            "time": time,
            "tz": tz
        },
        "status": "ok"
    }
