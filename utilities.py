import pandas as pd
import re
import streamlit as st

def extract_damage_value(damage_str):
    if pd.isna(damage_str):
        return 0
    match = re.search(r'\$(\d+(?:,\d+)?(?:\.\d+)?)', damage_str)
    if match:
        return float(match.group(1).replace(',', ''))
    return 0

@st.cache_data
def load_crash_data():
    total_dataset = 13
    return pd.concat([pd.read_csv(f'crash_data_{i+1}.csv') for i in range(total_dataset)])

def extract_damage_value(damage_str):
    if pd.isna(damage_str) or not isinstance(damage_str, str):
        return 0
    damage_str = damage_str.replace('$', '').replace(',', '').strip()
    try:
        return int(damage_str)
    except ValueError:
        return 0

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
def filter_data(df, start_date, end_date, weather, severity):
    filtered = df[(df['CRASH_DATE'] >= pd.to_datetime(start_date)) & (df['CRASH_DATE'] <= pd.to_datetime(end_date))]
    if weather != 'All':
        filtered = filtered[filtered['WEATHER_CONDITION'] == weather]
    if severity == 'Minor':
        filtered = filtered[filtered['INJURIES_TOTAL'] == 0]
    elif severity == 'Severe':
        filtered = filtered[filtered['INJURIES_TOTAL'] > 0]
    elif severity == 'Moderate':
        # Example logic: between 1–3 injuries
        filtered = filtered[(filtered['INJURIES_TOTAL'] > 0) & (filtered['INJURIES_TOTAL'] <= 3)]
    return filtered

@st.cache_resource
def load_map_html():
    with open("chicago_map.html", "r", encoding="utf-8") as f:
        return f.read()
