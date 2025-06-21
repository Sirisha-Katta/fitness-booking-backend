from datetime import datetime
import pytz

def convert_class_timezone(cls: dict, to_timezone: str):
    from_zone = pytz.timezone("Asia/Kolkata")
    to_zone = pytz.timezone(to_timezone)
    # Parse the string to a datetime object
    dt = datetime.strptime(cls["datetime"], "%d/%m/%Y %H:%M:%S")
    dt = from_zone.localize(dt)
    utc_dt = dt.astimezone(pytz.utc)
    converted_dt = utc_dt.astimezone(to_zone)
    cls["datetime"] = converted_dt
    return cls