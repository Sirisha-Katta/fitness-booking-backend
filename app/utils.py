from datetime import datetime
import pytz

from datetime import datetime
import pytz

def convert_class_timezone(cls, target_timezone):
    dt = cls["datetime"]

    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")  

    # Localize and convert timezone
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    target_tz = pytz.timezone(target_timezone)
    localized_dt = dt.astimezone(target_tz)

    # ✅ Return the datetime object itself — NOT formatted string
    return {
        **cls,
        "datetime": localized_dt
    }

