import streamlit as st
import pandas as pd
from pandas import DataFrame

def get_customer_search(order_col, customer_id: int) -> DataFrame | dict:
    results = order_col.find({'customer_id': customer_id})
    order_of_customer = [result for result in results]
    order_of_customer_df = pd.DataFrame(order_of_customer).explode("order_list")
    COLUMN_CONFIG = {
            "_id": "Order id", 
            "customer_id": "Customer id",
            "order_timestamp": st.column_config.DateColumn(
            "Order timestamp",
                    format ="DD.MM.YYYY",
            ),
            "order_list": "Order List"
    }

    return order_of_customer_df, COLUMN_CONFIG