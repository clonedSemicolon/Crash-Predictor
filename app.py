import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from utilities import extract_damage_value
import plotly.express as px
from sklearn.cluster import KMeans
import folium

# Set page configuration with reduced padding
st.set_page_config(page_title="Chicago Crash Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to improve padding and layout
st.markdown("""
<style>
    body {
        color: #fff;
        background-color: #0e1117;
        padding: 0;
    }
    .stApp {
        max-width: 100%;
        margin: 0 auto;
    }
    .metric-card {
        background-color: #1c1f26;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4cc9f0;
    }
    .metric-label {
        font-size: 1rem;
        color: #a0aec0;
    }
    .chart-container {
        background-color: #1c1f26;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #fff;
    }
    .stSelectbox, .stSlider {
        background-color: #1c1f26;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard title
st.title("Chicago Crash Dashboard")

# Load data
total_dataset = 13
combined_df = pd.concat([pd.read_csv(f'crash_data_{i + 1}.csv') for i in range(total_dataset)])

# Calculate damage costs
combined_df['DAMAGE_VALUE'] = combined_df['DAMAGE'].apply(extract_damage_value)

def categorize_damage(value):
    if value <= 500:
        return "$0 - $500"
    elif value <= 1000:
        return "$501 - $1,000"
    elif value <= 1500:
        return "$1,001 - $1,500"
    else:
        return "Over $1,500"

combined_df['DAMAGE_CATEGORY'] = combined_df['DAMAGE_VALUE'].apply(categorize_damage)
total_damage = combined_df['DAMAGE_VALUE'].sum()

# st.write(combined_df.columns)

# Sidebar Filters
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input("End Date", pd.to_datetime('2025-01-01'))
weather_condition = st.sidebar.selectbox("Select Weather Condition", ['All'] + list(combined_df['WEATHER_CONDITION'].unique()))
severity = st.sidebar.selectbox("Select Crash Severity", ['All', 'Minor', 'Moderate', 'Severe'])

combined_df['CRASH_DATE'] = pd.to_datetime(combined_df['CRASH_DATE'], errors='coerce')


# Apply Filters
filtered_df = combined_df[(combined_df['CRASH_DATE'] >= pd.to_datetime(start_date)) & (combined_df['CRASH_DATE'] <= pd.to_datetime(end_date))]

if weather_condition != 'All':
    filtered_df = filtered_df[filtered_df['WEATHER_CONDITION'] == weather_condition]

if severity != 'All':
    filtered_df = filtered_df[filtered_df['INJURIES_TOTAL'] > 0 if severity == 'Severe' else (filtered_df['INJURIES_TOTAL'] == 0 if severity == 'Minor' else filtered_df['INJURIES_TOTAL'] > 0)]

# Layout for metrics
col1, col2, col3 = st.columns([2, 3, 3])

with col1:
    st.markdown("### Key Metrics")
    
    total_crashes = len(filtered_df)
    total_injuries = filtered_df['INJURIES_TOTAL'].sum()
    avg_speed_limit = filtered_df['POSTED_SPEED_LIMIT'].mean()

    metrics = [
        ("Total Crashes", f"{total_crashes:,}"),
        ("Total Injuries", f"{total_injuries:,}"),
        ("Avg Speed Limit", f"{avg_speed_limit:.1f} mph"),
        ("Total Damage Cost", f"${total_damage:,.2f}")
    ]

    for label, value in metrics:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")  # Add some space between cards
    
with col2:
    st.markdown("### Crash Severity Breakdown")
    
    no_injuries_count = sum(filtered_df['INJURIES_TOTAL'] == 0)
    injuries_count = sum(filtered_df['INJURIES_TOTAL'] > 0)
    
    fig = go.Figure(data=[go.Pie(labels=['No Injuries', 'Injuries'],
                                 values=[no_injuries_count, injuries_count],
                                 hole=.3,
                                 marker_colors=['#4cc9f0', '#f72585'])])
    
    fig.update_layout(
        title_text="Crashes with Injuries vs No Injuries",
        showlegend=True,
        legend_orientation="h",
        legend=dict(x=0.5, xanchor="center"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("### Economic Impact")
    damage_summary = filtered_df.groupby('DAMAGE_CATEGORY')['DAMAGE_VALUE'].sum().sort_values(ascending=True)
    fig = go.Figure(go.Bar(
        x=damage_summary.values,
        y=damage_summary.index,
        orientation='h',
        marker_color='#4cc9f0'
    ))
    fig.update_layout(
        title='Damage Cost by Category',
        xaxis_title='Total Damage Cost ($)',
        yaxis_title='Damage Category',
        font=dict(color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)  


st.markdown("### Crash Hotspot Map")
with open("chicago_map.html", "r", encoding="utf-8") as f:
    html_data = f.read()
components.html(html_data, height=700, scrolling=False) 

# Time-based analysis layout
st.markdown("### Time-based Analysis")

col4, col5 = st.columns(2)

with col4:
    st.markdown("#### Crashes by Hour")
    if 'CRASH_HOUR' in filtered_df.columns:
        hour_counts = filtered_df['CRASH_HOUR'].value_counts().sort_index()
        all_hours = pd.Series(range(24))
        hour_counts = hour_counts.reindex(all_hours, fill_value=0)

        fig = go.Figure(data=[go.Bar(x=hour_counts.index, y=hour_counts.values, marker_color='#4cc9f0')])
        fig.update_layout(
            title='Crashes by Hour of Day',
            xaxis_title='Hour',
            yaxis_title='Number of Crashes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickmode='array', tickvals=list(range(0, 24, 4)), ticktext=[f'{i:02d}:00' for i in range(0, 24, 4)]),
        )
        st.plotly_chart(fig, use_container_width=True)

with col5:
    st.markdown("#### Crashes by Month")
    if 'CRASH_MONTH' in filtered_df.columns:
        month_counts = filtered_df['CRASH_MONTH'].value_counts().sort_index()
        all_months = pd.Series(range(1, 13))
        month_counts = month_counts.reindex(all_months, fill_value=0)
        
        fig = go.Figure(data=[go.Bar(x=month_counts.index, y=month_counts.values, marker_color='#4cc9f0')])
        fig.update_layout(
            title='Crashes by Month',
            xaxis_title='Month',
            yaxis_title='Number of Crashes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        )
        st.plotly_chart(fig, use_container_width=True)

# Weather and Lighting Condition Breakdown
st.markdown("### Weather and Lighting Conditions")

col6, col7 = st.columns(2)

with col6:
    st.markdown("#### Weather Condition Breakdown")
    weather_counts = filtered_df['WEATHER_CONDITION'].value_counts()
    fig_weather = go.Figure(go.Bar(x=weather_counts.index, y=weather_counts.values, marker_color='#7209b7'))
    fig_weather.update_layout(title='Crashes by Weather Condition', xaxis_title='Weather', yaxis_title='Crashes', font=dict(color='white'),
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_weather, use_container_width=True)

with col7:
    st.markdown("#### Lighting Condition Breakdown")
    light_counts = filtered_df['LIGHTING_CONDITION'].value_counts()
    fig_light = go.Figure(go.Pie(labels=light_counts.index, values=light_counts.values, marker_colors=['#560bad','#f72585','#4cc9f0']))
    fig_light.update_layout(title='Lighting Conditions During Crashes', font=dict(color='white'),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_light, use_container_width=True)

# Downloadable Report Button
st.markdown("### Download Filtered Crash Data")
def download_button(df, button_text="Download Data as CSV"):
    csv = df.to_csv(index=False)
    st.download_button_


# Cluster by road type and severity (e.g., residential vs. arterial roads)
clustering_df = filtered_df[['TRAFFICWAY_TYPE', 'INJURIES_TOTAL']].dropna()

# Encode road type to numeric
clustering_df['ROADWAY_TYPE'] = clustering_df['TRAFFICWAY_TYPE'].astype('category').cat.codes

# Apply KMeans clustering
kmeans = KMeans(n_clusters=4, random_state=42)
clustering_df['Cluster'] = kmeans.fit_predict(clustering_df[['ROADWAY_TYPE', 'INJURIES_TOTAL']])

# Visualize the clusters
fig = go.Figure(go.Bar(
    x=clustering_df['Cluster'].value_counts().index,
    y=clustering_df['Cluster'].value_counts().values,
    marker_color='#f72585'
))
fig.update_layout(
    title='Crash Clusters by Road Type and Severity',
    xaxis_title='Cluster',
    yaxis_title='Number of Crashes',
    font=dict(color='white'),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)
