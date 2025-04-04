import streamlit as st
import pandas as pd
from pathlib import Path

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# Global event dictionary: name -> list of date strings
_event_dates = {}

# Run once on import: load all .txt files in /events
def _load_all_event_dates():
    event_dir = Path('./events')
    if not event_dir.exists():
        print("[Event Load] No ./events folder found.")
        return
    for path in event_dir.glob('*.txt'):
        name = path.stem
        with open(path, "r") as f:
            dates = [pd.to_datetime(line.strip()).date() for line in f if line.strip()]
            _event_dates[name] = dates
            print(f"[Event Load] {name}: {len(dates)} dates loaded")

_load_all_event_dates()

# --- Public API ---

def list_available_event_filters():
    """Return event filter names from loaded .txt files"""
    return sorted(_event_dates.keys())

def get_all_event_dates():
    """Return a union of all dates from all .txt files"""
    all_union = set()
    for dates in _event_dates.values():
        all_union.update(dates)
    return sorted(all_union)

def filter_dates_by_weekday(date_list, selected_days):
    """Return only dates matching selected weekdays"""
    day_map = {day: i for i, day in enumerate(WEEKDAYS)}
    selected_nums = {day_map[day] for day in selected_days}
    return [d for d in date_list if pd.to_datetime(d).weekday() in selected_nums]

def get_all_filter_checkboxes():
    selected_filters = []

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Weekdays & Daily**")
        if st.checkbox("Daily"):
            selected_filters.append("daily")
        for day in WEEKDAYS:
            if st.checkbox(day):
                selected_filters.append(day)

    with col2:
        st.markdown("**Event Filters**")
        for event in list_available_event_filters():
            if st.checkbox(event):
                selected_filters.append(event)

    return selected_filters

def compute_filtered_dates(all_dates, selected_filters):
    """Combine logic across weekday, daily, and event filters"""
    selected = set()

    if "daily" in selected_filters:
        selected.update(all_dates)
        print(f"[Filter] 'Daily' selected: {len(all_dates)} total dates.")

    weekdays = [f for f in selected_filters if f in WEEKDAYS]
    if weekdays:
        weekday_dates = filter_dates_by_weekday(all_dates, weekdays)
        selected.update(weekday_dates)
        print(f"[Filter] Weekdays selected ({weekdays}): {len(weekday_dates)} dates.")

    for event_name in selected_filters:
        if event_name in _event_dates:
            selected.update(_event_dates[event_name])
            print(f"[Filter] Event '{event_name}' added {len(_event_dates[event_name])} dates.")

    print(f"[Filter] Total unique selected dates: {len(selected)}")
    print(f"[Filter] Sample dates: {list(sorted(selected))[:5]}")

    return sorted(selected)
