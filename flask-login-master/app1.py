from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import os

# Load the trained model and preprocessing objects
MODEL_PATH = "model/carbon_footprint_model.pkl"
ENCODERS_PATH = "model/label_encoders.pkl"
SCALER_PATH = "model/scaler.pkl"

model = joblib.load(MODEL_PATH)
label_encoders = joblib.load(ENCODERS_PATH)
scaler = joblib.load(SCALER_PATH)

# Flask app setup
app = Flask(__name__)

# Define input form page
@app.route('/')
def home():
    return render_template('index.html')  # Form page

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse form data
        input_data = {
            'Body Type': request.form['body_type'],
            'Sex': request.form['sex'],
            'Diet': request.form['diet'],
            'How Often Shower': int(request.form['shower']),
            'Heating Energy Source': request.form['heating_energy_source'],
            'Transport': request.form['transport'],
            'Vehicle Type': request.form['vehicle_type'],
            'Social Activity': request.form['social_activity'],
            'Monthly Grocery Bill': float(request.form['grocery_bill']),
            'Frequency of Traveling by Air': request.form['air_travel'],
            'Vehicle Monthly Distance Km': float(request.form['vehicle_distance']),
            'Waste Bag Size': request.form['waste_bag_size'],
            'Waste Bag Weekly Count': float(request.form['waste_bag_count']),
            'How Long TV PC Daily Hour': float(request.form['tv_pc_hours']),
            'How Many New Clothes Monthly': float(request.form['new_clothes']),
            'How Long Internet Daily Hour': float(request.form['internet_hours']),
            'Energy efficiency': request.form['energy_efficiency']  # Corrected key
        }

        # Convert input data to DataFrame
        df = pd.DataFrame([input_data])

        # Debug: Print column names
        print("Input DataFrame columns:", df.columns.tolist())

        # Apply mappings and preprocessing
        mappings = {
            'Social Activity': {'often': 3, 'sometimes': 2, 'rarely': 1, 'never': 0},
            'Frequency of Traveling by Air': {'very frequently': 4, 'frequently': 3, 'rarely': 2, 'never': 1},
            'Waste Bag Size': {'small': 1, 'medium': 2, 'large': 3, 'extra large': 4},
            'How Often Shower': {'daily': 1, 'weekly': 7, 'monthly': 30},
            'Energy efficiency': {'No': 0, 'Sometimes': 1, 'Yes': 2}
        }
        for column, mapping in mappings.items():
            if column in df.columns:
                df[column] = df[column].map(mapping)

        # Label encode categorical features
        categorical_columns = ['Body Type', 'Sex', 'Diet', 'Transport', 'Vehicle Type', 'Heating Energy Source']
        for col in categorical_columns:
            if col in df.columns and col in label_encoders:
                df[col] = label_encoders[col].transform(df[col].astype(str))

        # Scale numerical columns
        numerical_columns = ['Monthly Grocery Bill', 'Vehicle Monthly Distance Km', 'Waste Bag Weekly Count',
                             'How Long TV PC Daily Hour', 'How Many New Clothes Monthly', 'How Long Internet Daily Hour']
        df[numerical_columns] = scaler.transform(df[numerical_columns])

        # Debug: Print processed DataFrame
        print("Processed DataFrame:\n", df)

        # Make prediction
        prediction = model.predict(df)
        result = prediction[0]

        return jsonify({'Carbon Emission': result})
    except Exception as e:
        return jsonify({'error': str(e)})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)