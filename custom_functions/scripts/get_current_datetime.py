import datetime


def get_current_datetime():
    return {"datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
