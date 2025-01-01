# modules/time_processing.py
def process_time(time_data):
    hour = time_data["datetime"].hour
    if hour < 12:
        part_of_day = "Morning"
    elif 12 <= hour < 18:
        part_of_day = "Afternoon"
    else:
        part_of_day = "Evening"

    return {
        "date": time_data["date"],
        "time": time_data["time"],
        "weekday": time_data["weekday"],
        "part_of_day": part_of_day,
    }
