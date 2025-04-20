import pandas as pd
import re
import streamlit as st
import time

@st.cache_data
def extract_damage_value(damage_str):
    if pd.isna(damage_str) or not isinstance(damage_str, str):
        return 0
    damage_str = damage_str.strip().upper()
    if "OVER" in damage_str:
        return 2000  # Estimate for "OVER $1,500"
    elif "OR LESS" in damage_str:
        return 250   # Estimate for "$500 OR LESS"
    elif "-" in damage_str:
        match = re.findall(r'\d+', damage_str.replace(',', ''))
        if len(match) == 2:
            low, high = map(int, match)
            return (low + high) // 2  # Use average
    return 0


@st.cache_data
def categorize_damage(value):
    if value <= 500:
        return "$0 - $500"
    elif value <= 1000:
        return "$501 - $1,000"
    elif value <= 1500:
        return "$1,001 - $1,500"
    else:
        return "Over $1,500"

@st.cache_data
def preprocess_crash_data(df):
    df['DAMAGE_VALUE'] = df['DAMAGE'].apply(extract_damage_value)
    df['DAMAGE_CATEGORY'] = df['DAMAGE_VALUE'].apply(categorize_damage)
    df['CRASH_DATE'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce')
    df['CRASH_MONTH'] = df['CRASH_DATE'].dt.month
    df['CRASH_HOUR'] = pd.to_datetime(df['CRASH_DATE'], errors='coerce').dt.hour
    return df

@st.cache_data
def load_crash_data_with_progress():
    dfs = []
    progress = st.progress(0)
    for i in range(13):
        dfs.append(pd.read_csv(f'crash_data_{i+1}.csv'))
        progress.progress((i+1)/13)
    return pd.concat(dfs)

def filter_data(df, start_date, end_date, weather, severity):
    filtered = df[(df['CRASH_DATE'] >= pd.to_datetime(start_date)) & (df['CRASH_DATE'] <= pd.to_datetime(end_date))]
    if weather != 'All':
        filtered = filtered[filtered['WEATHER_CONDITION'] == weather]
    if severity == 'Minor':
        filtered = filtered[filtered['INJURIES_TOTAL'] == 0]
    elif severity == 'Severe':
        filtered = filtered[filtered['INJURIES_TOTAL'] > 3]
    elif severity == 'Moderate':
        filtered = filtered[(filtered['INJURIES_TOTAL'] > 0) & (filtered['INJURIES_TOTAL'] <= 3)]
    return filtered

@st.cache_resource
def load_map_html():
    with open("chicago_map.html", "r", encoding="utf-8") as f:
        return f.read()


@st.cache_resource
def load_large_html_map():
    progress_placeholder = st.empty()
    for i in range(100):  # Simulate progress loading
        progress_placeholder.progress(i + 1)
        time.sleep(0.01)  # Adjust this if needed
    progress_placeholder.empty()
    
    with open("chicago_map.html", "r", encoding="utf-8") as f:
        return f.read()

