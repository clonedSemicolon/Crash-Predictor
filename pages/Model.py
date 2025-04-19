import streamlit as st
import joblib
import pandas as pd

# Load model and encoders
model = joblib.load('../model/random_forest/RFclassifier.joblib')
label_encoders = joblib.load('../model/random_forest/RF_encoders.joblib')

st.title('Crash Type Predictor')

# Input widgets
input_data = {}

# Define default values from the problem statement
default_values = {
    'ROAD_DEFECT': 'UNKNOWN',
    'MANEUVER': 'STRAIGHT AHEAD',
    'SEX': 'M'
}

# Create input fields
input_cols = [
    'POSTED_SPEED_LIMIT', 'WEATHER_CONDITION', 'LIGHTING_CONDITION',
    'TRAFFICWAY_TYPE', 'ALIGNMENT', 'ROADWAY_SURFACE_COND', 'ROAD_DEFECT',
    'PRIM_CONTRIBUTORY_CAUSE', 'SEC_CONTRIBUTORY_CAUSE', 'CRASH_HOUR',
    'CRASH_DAY_OF_WEEK', 'CRASH_MONTH', 'MANEUVER', 'SEX', 'AGE'
]

for col in input_cols:
    le = label_encoders[col]
    options = list(le.classes_)

    # Set default value if specified
    default_val = default_values.get(col, options[0])
    if default_val in options:
        index = options.index(default_val)
    else:
        index = 0

    input_data[col] = st.selectbox(
        label=f"{col.replace('_', ' ').title()}",
        options=options,
        index=index
    )

# Prediction logic
if st.button('Predict Crash Type'):
    # Encode inputs
    encoded_input = {}
    for col in input_cols:
        le = label_encoders[col]
        encoded_value = le.transform([input_data[col]])[0]
        encoded_input[col] = encoded_value

    # Create DataFrame and predict
    input_df = pd.DataFrame([encoded_input])
    prediction = model.predict(input_df)

    # Decode prediction
    target_encoder = label_encoders['FIRST_CRASH_TYPE']
    predicted_crash_type = target_encoder.inverse_transform(prediction)[0]

    st.subheader(f"Predicted Crash Type: {predicted_crash_type}")
