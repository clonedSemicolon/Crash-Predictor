import streamlit as st
import pandas as pd
import joblib
import time 
import numpy as np

# Load trained model and encoders
model = joblib.load('./models/riskModel/model.pkl')
encoders = joblib.load('./models/riskModel/encoders.pkl')
target_encoder = joblib.load('./models/riskModel/target_encoder.pkl')

st.markdown("""
    <style>
    body { background-color: #121212; color: white; }
    .stApp { background-color: #121212; }
    .css-1d391kg { color: white; }
    .stSlider > div > div > div > div { background-color: #333; }
    </style>
""", unsafe_allow_html=True)

st.title("🚦 Accident Risk Predictor")
st.markdown("""
Predict the **risk level** of a traffic accident based on real-time crash data.
Enter the conditions below to assess the likelihood of **Low**, **Medium**, or **High** risk.
""")

# --- User Inputs ---
weather = st.selectbox("🌦️ Weather Condition", encoders['WEATHER_CONDITION'].classes_)
lighting = st.selectbox("💡 Lighting Condition", encoders['LIGHTING_CONDITION'].classes_)
road_surface = st.selectbox("🛣️ Road Surface Condition", encoders['ROADWAY_SURFACE_COND'].classes_)
speed_limit = st.slider("🚗 Posted Speed Limit (mph)", 5, 70, 30, step=5)
damage_value = st.slider("💥 Estimated Damage Value ($)", 0, 10000, 1500, step=100)
num_units = st.slider("🚘 Number of Units Involved", 1, 10, 2)
crash_hour = st.slider("🕒 Crash Hour (0-23)", 0, 23, 12)
crash_type = st.selectbox("🔄 First Crash Type", encoders['FIRST_CRASH_TYPE'].classes_)

if st.button("🔍 Predict Risk Level"):
    with st.spinner("Analyzing accident risk..."):
        time.sleep(1.5)  # Simulate processing

    input_data = pd.DataFrame([{ 
        'POSTED_SPEED_LIMIT': speed_limit,
        'WEATHER_CONDITION': encoders['WEATHER_CONDITION'].transform([weather])[0],
        'LIGHTING_CONDITION': encoders['LIGHTING_CONDITION'].transform([lighting])[0],
        'ROADWAY_SURFACE_COND': encoders['ROADWAY_SURFACE_COND'].transform([road_surface])[0],
        'DAMAGE_VALUE': damage_value,
        'NUM_UNITS': num_units,
        'CRASH_HOUR': crash_hour,
        'FIRST_CRASH_TYPE': encoders['FIRST_CRASH_TYPE'].transform([crash_type])[0]
    }])

    prediction = model.predict(input_data)[0]
    risk_label = target_encoder.inverse_transform([prediction])[0]

    # Risk messages
    if risk_label == "High":
        st.error("⚠️ High Risk: Severe crash likely with injuries or major damage. Immediate response recommended.")
    elif risk_label == "Medium":
        st.warning("🚧 Medium Risk: Possibility of injury or moderate damage. Exercise caution.")
    else:
        st.success("✅ Low Risk: Minor crash scenario. Risk level is low, but stay alert.")

    st.markdown(f"### 🧠 Predicted Risk Level: **{risk_label.upper()}**")

    # Feature Importance (manual approximation)
    feature_names = ['POSTED_SPEED_LIMIT', 'WEATHER_CONDITION', 'LIGHTING_CONDITION', 'ROADWAY_SURFACE_COND',
                    'DAMAGE_VALUE', 'NUM_UNITS', 'CRASH_HOUR', 'FIRST_CRASH_TYPE']
    importances = model.feature_importances_
    top_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:3]

    # Driving tips
    st.markdown("---")
    st.subheader("🛡️ Safety Tip for Drivers")
    tip = np.random.choice([
        "Keep a safe distance from the vehicle in front of you.",
        "Slow down in poor weather or lighting conditions.",
        "Avoid distractions like phones while driving.",
        "Always wear your seatbelt.",
        "Adjust speed when approaching intersections.",
        "Be extra alert during night driving hours."
    ])
    st.info(f"💡 {tip}")



# --- Policy Suggestions based on inputs ---
    st.markdown("---")
    st.subheader("📊 Policy Recommendations for This Crash Scenario")

    suggestions = []

    # SPEED policy
    if speed_limit >= 45:
        suggestions.append(f"🔻 Consider reducing the **speed limit** from {speed_limit} mph to around {speed_limit - 10} mph in this area.")
    elif speed_limit < 25:
        suggestions.append("✅ Speed limit appears to be relatively safe based on model patterns.")

    # LIGHTING policy
    if "DARK" in lighting.upper() or "NO LIGHTING" in lighting.upper():
        suggestions.append("💡 Improve **street lighting** in this location to reduce the chance of severe crashes.")

    # DAMAGE
    if damage_value >= 2000:
        suggestions.append("💥 Encourage safer driving behaviors or install traffic calming measures to reduce damage severity.")

    # CRASH HOUR
    if crash_hour in [0, 1, 2, 3, 23]:
        suggestions.append("🌙 Increased monitoring recommended during late night hours (11PM–3AM) due to heightened risk.")

    # CRASH TYPE
    if "REAR" in crash_type.upper():
        suggestions.append("🚘 Consider campaigns or signage against tailgating in this zone — frequent rear-end crashes detected.")

    # Feature-based explanation
    st.markdown("### 🔍 Model Insight:")
    top_feat_text = ", ".join([f"`{name}`" for name, _ in top_features])
    st.markdown(f"Based on the model, the most influential factors in this prediction were: {top_feat_text}.")

    if suggestions:
        st.markdown("### 📌 Recommended Actions:")
        for s in suggestions:
            st.write(s)
    else:
        st.success("✅ No critical policy actions needed for this scenario. Conditions appear within low-risk thresholds.")
