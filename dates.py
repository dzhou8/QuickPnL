import streamlit as st
import pandas as pd
from pathlib import Path

# Filter a list of dates by selected weekdays
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

# Load event dates from a .txt file in /events
def load_event_dates(event_name):
    path = Path(f"./events/{event_name}.txt")
    if not path.exists():
        return []
    with open(path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

# Discover all available filters based on .txt files in /events
def list_available_event_filters():
    event_dir = Path('./events')
    if not event_dir.exists():
        return []
    return sorted([f.stem for f in event_dir.glob('*.txt')])

# Central logic to get a combined list of dates based on selected filters
def get_filtered_dates(all_dates, selected_filters):
    selected = set()

    if "daily" in selected_filters:
        selected.update(all_dates)

    weekdays = [f for f in selected_filters if f in {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}]
    if weekdays:
        selected.update(filter_dates_by_weekday(all_dates, weekdays))

    for event_name in selected_filters:
        if event_name not in {"daily", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}:
            selected.update(load_event_dates(event_name))

    return sorted(selected)

# Generate checkboxes and return the selected filter labels
def get_all_filter_checkboxes():
    selected_filters = []

    if st.checkbox("Daily"):
        selected_filters.append("daily")

    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        if st.checkbox(day):
            selected_filters.append(day)

    st.subheader("Event Filters")
    for event in list_available_event_filters():
        if st.checkbox(event):
            selected_filters.append(event)

    return selected_filters