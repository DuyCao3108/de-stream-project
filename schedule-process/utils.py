import pandas as pd
import psycopg2

# PostgreSQL connection parameters
host = "172.25.32.171"
database = "postgres"
user = "postgres"
password = "example"

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)

def get_product_infos(product_id: int) -> dict:
    cursor = conn.cursor()
    command = f"""
        SELECT * FROM public.product
        WHERE product_id = {str(product_id)}
    """
    cursor.execute(command)  # Execute the SQL command
    result = cursor.fetchone()  # Fetch one row
    column_names = [desc[0] for desc in cursor.description]  # Get column names
    product_info = dict(zip(column_names, result))  # Create a dictionary of product info
    return product_info


