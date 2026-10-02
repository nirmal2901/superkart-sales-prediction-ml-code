
# Import necessary libraries
import numpy as np
import joblib
import pandas as pd
import datetime
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_sales_api = Flask("SuperKart Sales Prediction API")

# Load the trained machine learning pipeline
model = joblib.load("Superkart_sales_prediction_model_v1_0.joblib")

# Define perishable product types
perishables = [
    'Dairy', 'Meat', 'Seafood',
    'Fruits and Vegetables', 'Breads',
    'Frozen Foods', 'Breakfast'
]

# Define a route for the home page (GET request)
@superkart_sales_api.get('/')
def home():
    return "✅ Welcome to the SuperKart Sales Prediction API! Use POST /v1/sales to predict."

# Define an endpoint for single sales prediction (POST request)
@superkart_sales_api.post('/v1/sales')
def predict_sales():
    input_data = request.get_json()

    # Calculate engineered features
    current_year = datetime.datetime.now().year
    store_age = current_year - input_data['Store_Establishment_Year']
    product_id_char = input_data.get('Product_Id', 'P0000')[:2]
    product_type_category = 'Perishables' if input_data['Product_Type'] in perishables else 'Non Perishables'

    # Construct a sample input row with required fields
    sample = {
        'Product_Weight': input_data['Product_Weight'],
        'Product_Sugar_Content': input_data['Product_Sugar_Content'],
        'Product_Allocated_Area': input_data['Product_Allocated_Area'],
        'Product_Type': input_data['Product_Type'],
        'Product_Type_Category': product_type_category,       # ← new
        'Product_MRP': input_data['Product_MRP'],
        'Store_Establishment_Year': input_data['Store_Establishment_Year'],
        'Store_Age_Years': store_age,                         # ← new
        'Store_Size': input_data['Store_Size'],
        'Store_Location_City_Type': input_data['Store_Location_City_Type'],
        'Store_Type': input_data['Store_Type'],
        'Product_Id': 'P0000',                                # dummy
        'Product_Id_char': product_id_char,                   # ← new
        'Store_Id': 'S000',                                   # dummy
        'Product_Store_Sales_Total': 0                        # dummy
    }

    input_df = pd.DataFrame([sample])
    predicted_sales = model.predict(input_df)[0]
    predicted_sales = round(float(predicted_sales), 2)

    return jsonify({'Predicted sales (in dollars)': predicted_sales})

# Define an endpoint for batch sales prediction (CSV file upload)
@superkart_sales_api.post('/v1/salesbatch')
def predict_sales_batch():
    file = request.files['file']
    input_df = pd.read_csv(file)

    # Calculate engineered features for batch
    current_year = datetime.datetime.now().year
    input_df['Product_Id_char'] = input_df['Product_Id'].str[:2]                                              # ← new
    input_df['Store_Age_Years'] = current_year - input_df['Store_Establishment_Year']                         # ← new
    input_df['Product_Type_Category'] = input_df['Product_Type'].apply(
        lambda x: 'Perishables' if x in perishables else 'Non Perishables'
    )                                                                                                          # ← new

    # Make predictions
    predicted_sales = model.predict(input_df)
    predicted_sales = [round(float(val), 2) for val in predicted_sales]

    # Assume 'Product_Id' + 'Store_Id' combination for unique key
    keys = (input_df['Product_Id'] + '_' + input_df['Store_Id']).tolist()
    results = dict(zip(keys, predicted_sales))

    return jsonify(results)

# Run the Flask application
if __name__ == '__main__':
    superkart_sales_api.run(debug=True)
