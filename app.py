# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

total_dataset = 13

# Set page title and configuration
st.set_page_config(page_title="Chicago Crash Dashboard", layout="wide")

# Add dashboard title
st.title("Chicago Crash Dashboard")

# Create a more compact layout with multiple areas
col1, col2, col3 = st.columns([1, 2, 3])

# Left column will contain multiple components stacked vertically
with col1:
    # Create a container for the first chart component
    chart_container = st.container()
    
    with chart_container:
        combined_df = pd.DataFrame()

        # Read data from local CSV files
        for i in range(total_dataset):
            df = pd.read_csv(f'crash_data_{i + 1}.csv')
            combined_df = pd.concat([combined_df, df])

        # Count injuries and no injuries
        no_injuries_count = sum(combined_df['INJURIES_TOTAL'] == 0)
        injuries_count = sum(combined_df['INJURIES_TOTAL'] > 0)

        # Create data for the plot
        categories = ['No Injuries', 'Injuries']
        counts = [no_injuries_count, injuries_count]

        # Format counts as K format for display
        def format_k(x):
            if x >= 1000:
                return f"{x/1000:.2f}K"
            return str(x)

        formatted_counts = [format_k(count) for count in counts]

        # Create a small plot for corner placement
        fig, ax = plt.subplots(figsize=(2, 2))  # Smaller size for corner component

        # Create narrower x positions to reduce gap
        x_pos = np.array([0, 0.6])  # Reduced gap between bars

        # Plot the data - blue bars with reduced gap
        bars = ax.bar(x_pos, counts, color='#1f77b4', width=0.4)

        # Set the x-tick positions and labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, fontsize=4, fontweight='bold')

        # Add the formatted count inside each bar
        for bar, count in zip(bars, formatted_counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                    count, ha='center', va='center', color='white', fontsize=6, fontweight='bold')

        # Add title and remove axis labels
        ax.set_title('Common Type of Crash', fontsize=6, fontweight='bold')
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_ylabel('')  # Remove y-axis label

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)  # Optionally remove left spine too for cleaner look

        # Hide y-axis ticks
        ax.tick_params(axis='y', which='both', left=False, labelleft=False)

        # Set x-axis limits to center the bars and control spacing
        ax.set_xlim(-0.2, 1.2)

        # Tight layout to minimize margins within the figure
        plt.tight_layout()

        # Display the plot as a component in the container
        st.pyplot(fig, use_container_width=False)  # Not using container width to keep it small
        
    # Space for additional components in the left column
    st.write("")  # Empty space
    # You can add more components below this point
    
# Create a layout in the right column for the three vertical cards
with col2:
    # Calculate metrics for the cards
    total_crashes = len(combined_df)
    total_injuries = combined_df['INJURIES_TOTAL'].sum()
    avg_speed_limit = combined_df['POSTED_SPEED_LIMIT'].mean()
    
    # Format the metrics for display
    formatted_total_crashes = format_k(total_crashes)
    formatted_total_injuries = format_k(total_injuries)
    formatted_avg_speed = f"{avg_speed_limit:.1f}"
    
    # Card descriptions
    crash_description = "Total number of crash incidents in Chicago across all datasets."
    injury_description = "Sum of all injuries reported in the crash incidents."
    speed_description = "Average posted speed limit across all crash locations."
    
    # Create a fixed-width container for the cards
    # Use a wider column for the cards to increase their size
    left_padding, cards_col, right_padding = st.columns([0.05, 0.7, 0.25])
    
    # Apply custom CSS for better-looking cards
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin: 0px 0px 16px 0px;
    }
    .metric-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #5a5c69;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .metric-description {
        font-size: 0.9rem;
        color: #6c757d;
        text-align: left;
        margin-top: 8px;
        line-height: 1.3;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display all cards in the middle column, stacked vertically
    with cards_col:
        # Card 1: Total Crashes
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Crashes</div>
            <div class="metric-value">{formatted_total_crashes}</div>
            <div class="metric-description">{crash_description}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 2: Total Injuries
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Injuries</div>
            <div class="metric-value">{formatted_total_injuries}</div>
            <div class="metric-description">{injury_description}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Card 3: Average Speed Limit
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Speed Limit</div>
            <div class="metric-value">{formatted_avg_speed} mph</div>
            <div class="metric-description">{speed_description}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # The remaining space in the right column can be used for other content
    with right_padding:
        pass

# Third column with time-based visualizations
with col3:

    # Extract year from CRASH_DATE if it exists
    if 'CRASH_DATE' in combined_df.columns:
        try:
            combined_df['CRASH_YEAR'] = pd.to_datetime(combined_df['CRASH_DATE']).dt.year
        except:
            combined_df['CRASH_YEAR'] = 0

    # By Hour Visualization
    st.markdown("<h5 style='color:#FFFFFF; font-weight:bold;'>Crashes in Hours</h5>", unsafe_allow_html=True)
    if 'CRASH_HOUR' in combined_df.columns:
        hour_counts = combined_df['CRASH_HOUR'].value_counts().sort_index()
        all_hours = pd.Series(range(24))
        hour_counts = hour_counts.reindex(all_hours, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 3))
        bars = ax.bar(hour_counts.index, hour_counts.values, color='#1f77b4', alpha=0.9)
        ax.set_xticks(range(0, 24, 5))
        ax.set_yticks([0, 25000, 50000])
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False, labelleft=False)
        st.pyplot(fig)

    # By Month Visualization
    st.markdown("<h5 style='color:#FFFFFF; font-weight:bold;'>Crashes in Month</h5>", unsafe_allow_html=True)
    if 'CRASH_MONTH' in combined_df.columns:
        month_counts = combined_df['CRASH_MONTH'].value_counts().sort_index()
        all_months = pd.Series(range(1, 13))
        month_counts = month_counts.reindex(all_months, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 3))
        bars = ax.bar(month_counts.index, month_counts.values, color='#1f77b4', alpha=0.9)
        ax.set_xticks(range(1, 13))
        ax.set_yticks([0, 25000, 50000])
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False, labelleft=False)
        st.pyplot(fig)

    # By Year Visualization
    st.markdown("<h5 style='color:white; font-weight:bold;'>Crashes in Year</h5>", unsafe_allow_html=True)

    if 'CRASH_YEAR' in combined_df.columns and not all(combined_df['CRASH_YEAR'] == 0):
        
        # Count crashes per year and sort by year
        year_counts = combined_df['CRASH_YEAR'].value_counts().sort_index()

         # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 2))

        # Fill area under the curve
        ax.fill_between(year_counts.index, year_counts.values, color='#1f77b4', alpha=0.8)

        # Plot line graph
        ax.plot(year_counts.index, year_counts.values, color='#1f77b4', linewidth=2)

        # Customize x-axis and y-axis ticks
        ax.set_xticks(year_counts.index[::2])  # Show every other year on x-axis
        ax.set_yticks([0, 100000])  # Match y-axis ticks from image

        # Add gridlines for y-axis only
        ax.grid(axis='y', linestyle='--', alpha=0.5, color='white')

        # Remove spines for a clean look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('white')  # Keep bottom spine visible but styled

        # Remove left y-axis ticks and labels
        ax.tick_params(left=False, labelleft=False)

        # Set title with white color and bold font
        ax.set_title('Crashes in Year', fontsize=12, fontweight='bold', color='white')

        # Set background color to match dark theme
        fig.patch.set_facecolor('#ffffff')
        ax.set_facecolor('#ffffff')

        # Show plot in Streamlit app
        st.pyplot(fig)

