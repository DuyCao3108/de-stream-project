import pandas as pd

def read_csv_and_take_first_n_rows(file_path: str, n: int) -> pd.DataFrame:
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Take only the first n rows
    df_first_n_rows = df.head(n)
    
    return df_first_n_rows

# Example usage
file_path = "storage/product.csv"  # Specify the path to your CSV file
n_rows_to_take = 1000
first_1000_rows = read_csv_and_take_first_n_rows(file_path, n_rows_to_take)

first_1000_rows.to_csv("storage/product.csv", index=0)