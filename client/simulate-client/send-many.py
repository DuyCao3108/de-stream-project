import pandas as pd
import random
import requests
import json
import time
from datetime import datetime

# Read customer and product data from CSV files
customers_df = pd.read_csv('storage/customer_data.csv')
products_df = pd.read_csv('storage/product.csv')

# API endpoint
url = "http://localhost:80/order/"

# Function to generate a random order
def generate_random_order():
    # Select a random customer and product
    customer = customers_df.sample(n=1).iloc[0]
    product = products_df.sample(n=1).iloc[0]
    
    # Create order payload
    order_payload = {
        "customer_id": int(customer['customer_id']),
        "order_list": [
            {
                "product_id": int(product['product_id']),
                "quantity": random.randint(1, 10)  # Random quantity between 1 and 10
            },
            {
                "product_id": int(product['product_id']),
                "quantity": random.randint(1, 10)  # Random quantity between 1 and 10
            }
        ],
        "order_timestamp": str(datetime.now())
    }
    
    return order_payload

# Function to send order through API
def send_order(order_payload):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python Script"
    }
    
    response = requests.post(url, json=order_payload, headers=headers)
    return response.text

# Loop to send 100 orders
while True:
    order = generate_random_order()
    response = send_order(order)
    print(response)
    # Sleep for 1 second
    time.sleep(1)
