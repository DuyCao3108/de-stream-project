import pandas as pd
from faker import Faker

# Initialize Faker
fake = Faker()

# Generate customer data
num_customers = 100
customer_data = [{'customer_id': i+1, 'customer_name': fake.name()} for i in range(num_customers)]
customer_df = pd.DataFrame(customer_data)

# Generate product data
num_products = 50
product_data = [{'product_id': i+1, 
                 'product_name': fake.word(), 
                 'product_category': fake.word(),
                 'price': fake.random_number(digits=2)} for i in range(num_products)]
product_df = pd.DataFrame(product_data)

# Save dataframes to CSV files
customer_df.to_csv('./storage/customer_data.csv', index=False)
product_df.to_csv('./storage/product_data.csv', index=False)

print("Data saved to CSV files: customer_data.csv and product_data.csv")
