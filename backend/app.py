import pandas as pd
from sklearn.linear_model import LinearRegression
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'user': 'root',
    'password': 'Ashray@8571',
    'host': 'localhost',
    'database': 'saled_db'
}

# Create a database connection
def create_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Route to fetch sales data
@app.route('/api/sales', methods=['GET'])
def get_sales_data():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sales)

# Route to perform predictive analysis
@app.route('/api/predict', methods=['POST'])
def predict_sales():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch sales data
    cursor.execute("SELECT product_id, customer_id, quantity_sold, sale_date FROM sales")
    sales_data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert sales data to a DataFrame
    df = pd.DataFrame(sales_data)
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df['sale_year'] = df['sale_date'].dt.year
    df['sale_month'] = df['sale_date'].dt.month

    # Prepare the features and target variable
    X = df[['product_id', 'customer_id', 'sale_year', 'sale_month']]
    y = df['quantity_sold']

    # Train a simple linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Get input data for prediction from the request
    input_data = request.json
    input_df = pd.DataFrame([input_data])

    # Perform the prediction
    predicted_sales = model.predict(input_df[['product_id', 'customer_id', 'sale_year', 'sale_month']])
    
    return jsonify({'predicted_sales': round(predicted_sales[0])})

if __name__ == '__main__':
    app.run(debug=True)
