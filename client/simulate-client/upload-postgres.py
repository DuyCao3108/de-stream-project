import pandas as pd
import psycopg2

# Read customer and product data from CSV files
customers_df = pd.read_csv('storage/customer_data.csv')
products_df = pd.read_csv('storage/product.csv')

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

# Function to create tables
def create_tables(conn):
    cursor = conn.cursor()
    # Create customer table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.customer (
            customer_id INTEGER,
            customer_name TEXT NOT NULL,
            PRIMARY KEY (customer_id)
        );
    """)
    # Create product table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.product (
            product_id INTEGER,
            product_category TEXT NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            PRIMARY KEY (product_id)
        );
    """)
    # Commit changes
    conn.commit()
    cursor.close()

# Function to upload dataframe to PostgreSQL table without dropping
def upload_to_postgres(df, table_name, conn):
    cursor = conn.cursor()
    # Upload data
    for row in df.itertuples(index=False):
        placeholders = ', '.join(['%s' for _ in range(len(df.columns))])
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        cursor.execute(insert_query, row)
    # Commit changes
    conn.commit()
    cursor.close()

# Create tables
create_tables(conn)

# Upload customer data to PostgreSQL (append)
upload_to_postgres(customers_df, 'public.customer', conn)

# Upload product data to PostgreSQL (append)
upload_to_postgres(products_df, 'public.product', conn)

# Close the connection
conn.close()

print("Data appended to PostgreSQL tables: customer and product")
