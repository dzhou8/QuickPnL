import pandas as pd

def filter_dates_by_weekday(date_list, selected_days):
    day_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4
    }
    selected_nums = {day_map[day] for day in selected_days}
    return [d for d in date_list if pd.to_datetime(d).weekday() in selected_nums]
