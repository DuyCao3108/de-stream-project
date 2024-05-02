import pymongo
import pymongo.collation
import pymongo.collection

def get_cur_kpi(order_col: pymongo.collection, query: dict = None) -> dict: 
    orders = order_col.find(query)
    # init kpis
    num_order = 0
    sales = 0
    distinct_cust_dict = {}
    for order in orders:
        # calculate num_order
        num_order += 1
        # calculate sales
        order_value = 0
        for item_list in order['order_list']:
            item = item_list[0]
            order_value += float(item['quantity']) * float(item['price'])
        sales += order_value
        # calculate num cust
        if order['customer_id'] not in distinct_cust_dict: distinct_cust_dict[order['customer_id']] = 1
    num_cust = len(distinct_cust_dict.keys())
    # combine to kpi_dict
    kpi_dict = {
        "num_order": num_order,
        "sales": sales,
        "num_cust": num_cust
    }
    return kpi_dict

def retrieve_last_kpi(kpis_col: pymongo.collection):
    last_kpi_dict = kpis_col.find_one({})
    return last_kpi_dict

def calculate_kpi_change(current_kpi: dict, last_kpi: dict) -> dict:
    kpi_change_dict = {}
    for metric, current_value in current_kpi.items():
        last_value = last_kpi.get(metric, 0)  # Default to 0 if metric not found in last KPI
        change = (current_value - last_value) / last_value
        kpi_change_dict[metric] = change * 100
    return kpi_change_dict

def delete_kpi_col(kpis_col: pymongo.collection) -> None:
    kpis_col.delete_many()

def store_cur_kpi(cur_kpi_dict: dict, kpis_col: pymongo.collection) -> True | False:
    kpis_col.insert_one(cur_kpi_dict)

