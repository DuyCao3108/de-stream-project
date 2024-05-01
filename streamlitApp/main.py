from numpy import double
import streamlit as st
from pandas import DataFrame
import json
import numpy as np
import pymongo
import pandas as pd
from datetime import datetime, timedelta, timezone
import matplotlib as plt

from get_kpi import get_cur_kpi
from product_tab import get_category_df, get_surging_product_settings
from customer_tab import get_customer_search

# layout
st.title("Streaming Dashboard")
kpi_container = st.container()
kpi_sale, kpi_num_order, kpi_num_cust = kpi_container.columns(3)
tab_product, tab_customer = st.tabs(["Products", "Customers"])


# get col
myclient = pymongo.MongoClient("mongodb://localhost:27017/",username='duycao',password='123')
mydb = myclient["streaming_project"]
order_col = mydb["orders"] 
item_counts_col = mydb["item_counts"] 
surging_col = mydb["surging"] 
kpis_col =  mydb["kpis"] 


# render kpi
cur_kpi_dict = get_cur_kpi(order_col)
kpi_sale.metric("Sales", cur_kpi_dict['sales'], "3%")
kpi_num_order.metric("Orders", cur_kpi_dict['num_order'], "5%")
kpi_num_cust.metric("Distinct Customers", cur_kpi_dict['num_cust'], "-4%")


# render product tab
with tab_product:
    surging_product = tab_product.container()
    category = tab_product.container()
    with category:
        category.subheader("Value of category over time")
        cate_df = get_category_df(order_col)
        st.line_chart(cate_df, x = "order_day", y = "order_value", color = "product_category") 
    with surging_product:
        surging_product.subheader("Products that are surging in demand")
        surging_items_df, COLUMN_CONFIG = get_surging_product_settings(surging_col)
        st.dataframe(
            surging_items_df,
            column_config = COLUMN_CONFIG,
            hide_index = True,
            use_container_width = True
        )

# render customer tab
with tab_customer:
    search_order = tab_customer.container()
    with search_order:
        search_order.subheader("See order history of customers")
        customer_id_query = st.number_input("Customer_id: ")
        if not customer_id_query:
            customer_id_query = 2
        order_of_customer_df, COLUMN_CONFIG = get_customer_search(order_col, customer_id = customer_id_query)
        st.dataframe(
                order_of_customer_df,
                column_config = COLUMN_CONFIG,
                hide_index = True,
                use_container_width= True
        )





