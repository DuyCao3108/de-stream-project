import pandas as pd
from pandas import DataFrame
from typing import Union
import streamlit as st

def get_category_df(order_col) -> DataFrame:
    orders = order_col.find()
    category_table_list = []
    for order in orders:
        for item_list in order['order_list']:
            item = item_list[0] # item is list type, thus have to talke first ith of the list
            order_value = float(item['quantity']) * float(item['price'])
            category_table_list.append({
                "product_category": item['product_category'],
                "order_timestamp": order['order_timestamp'],
                "order_value": order_value 
            })    
    cate_df = pd.DataFrame(category_table_list)
    cate_df['order_timestamp'] = pd.to_datetime(cate_df['order_timestamp']) 
    cate_df['order_day'] = cate_df['order_timestamp'].apply(lambda x: x.strftime("%y-%m-%d: %H-%M"))
    # get accum value
    cate_df.sort_values(by='order_timestamp', inplace=True)
    cate_df['accumulated_value'] = cate_df['order_value'].cumsum()
    # filter on top 10 cate
    top10_cate = cate_df.sort_values(by="accumulated_value", ascending=False).head(10)['product_category'].unique()
    cate_df = cate_df[cate_df['product_category'].isin(top10_cate)]  
    # groupby order_day
    cate_df = cate_df.groupby(['product_category','order_day'])['order_value'].sum().reset_index()
    return cate_df

def get_surging_product_settings(surging_col) -> Union[DataFrame, dict]:
    surging_items = surging_col.find()
    surging_items_list = [surging_item for surging_item in surging_items]
    surging_items_df = pd.DataFrame(surging_items_list).drop(columns=['_id'])
    COLUMN_CONFIG = {
        "product_id": "Product id",
        "product_name": "Product name",
        "product_category": "Category",
        "historical_counts": st.column_config.LineChartColumn(
            "Purchases"
        )
    }

    return surging_items_df, COLUMN_CONFIG

