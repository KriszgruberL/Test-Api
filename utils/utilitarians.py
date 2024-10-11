from datetime import datetime, timezone, timedelta


def get_yesterday():


    # Calculate yesterday's date in UTC
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    # Format the date as 'Month Day, Year', e.g., 'October 12, 2023'
    date_str = yesterday.strftime('%B %d, %Y').lstrip('0').replace('\xa0', ' ')
    date_str = date_str.replace('\xa0', ' ')
    return yesterday, date_str

