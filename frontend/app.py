import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://localhost:7860"

# Set the title of the Streamlit app
st.title("🛒 SuperKart Sales Prediction")

# Section for online prediction
st.subheader("📦 Predict Sales for a Single Product")

# Collect user input
product_weight = st.number_input("Product Weight (in kg)", min_value=0.0, value=12.66)
sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])  # ← fixed values
allocated_area = st.number_input("Product Allocated Area", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f")  # ← fixed to number
product_type = st.selectbox("Product Type", [                                               # ← fixed values
    "Baking Goods", "Breads", "Breakfast", "Canned", "Dairy",
    "Frozen Foods", "Fruits and Vegetables", "Hard Drinks",
    "Health and Hygiene", "Household", "Meat", "Others",
    "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods"
])
product_mrp = st.number_input("Product MRP (₹)", min_value=1.0, value=117.08)
store_year = st.number_input("Store Establishment Year", min_value=1980, max_value=2026, value=2009)
store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
city_type = st.selectbox("City Type", ["Tier 1", "Tier 2", "Tier 3"])
store_type = st.selectbox("Store Type", [                                                   # ← fixed values
    "Supermarket Type1", "Supermarket Type2", "Supermarket Type3",
    "Departmental Store", "Food Mart"
])

# Prepare input data
input_data = pd.DataFrame([{
    'Product_Weight': product_weight,
    'Product_Sugar_Content': sugar_content,
    'Product_Allocated_Area': allocated_area,
    'Product_Type': product_type,
    'Product_MRP': product_mrp,
    'Store_Establishment_Year': store_year,
    'Store_Size': store_size,
    'Store_Location_City_Type': city_type,
    'Store_Type': store_type
}])

# Make prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/sales", json=input_data.to_dict(orient='records')[0])
    if response.status_code == 200:
        prediction = response.json()['Predicted sales (in dollars)']
        st.success(f"🧾 Predicted Sales: ₹{prediction}")
    else:
        st.error("❌ Error making prediction. Check backend logs.")

# Section for batch prediction
st.subheader("📂 Predict Sales for Multiple Products (Batch)")

# Allow users to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Make batch prediction when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        response = requests.post(f"{BACKEND_URL}/v1/salesbatch", files={"file": uploaded_file})
        if response.status_code == 200:
            predictions = response.json()
            st.success("✅ Batch prediction completed!")
            st.write(predictions)
        else:
            st.error("❌ Failed to process batch prediction.")
