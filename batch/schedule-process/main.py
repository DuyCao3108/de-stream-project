import pymongo.collation
import pymongo.collection
import schedule
import time
from datetime import datetime, timedelta, timezone
import pymongo
import numpy as np
from icecream import ic 
from utils import get_product_infos

# connect to db and col
myclient = pymongo.MongoClient("mongodb://IPADDRESS/",username='duycao',password='123')
mydb = myclient['streaming_project']
order_col = mydb['orders']
item_count_col = mydb['item_counts']
surging_col = mydb['surging']

# process global var
WINDOW = {"seconds": 33}
ANOMALY_THRESHOLD = 90

# schedule global var
RUN_TIMES = 3

# define sub-functions
def calculate_cur_item_counts(order_col: pymongo.collection, query: dict) -> dict:
    item_counts_dict = {}
    for order in order_col.find(query):
        ic(query, order)
        for item_list in order['order_list']:
            item = item_list[0] # item stored in document is list
            item_quantity = item['quantity']
            if item['product_id'] in item_counts_dict:
                item_counts_dict[item['product_id']] += item_quantity
            else:
                item_counts_dict[item['product_id']] = item_quantity
    return item_counts_dict

def store_cur_item_counts(item_count_col: pymongo.collection, item_counts_dict: dict) -> True | False:
    # storing new observation
    for item in item_counts_dict:
        historical_counts_of_item = item_count_col.find_one({"product_id": item})
        cur_counts_of_item = item_counts_dict[item]
        if historical_counts_of_item is None:
            try:
                product_info = get_product_infos(product_id = item)    
                item_count_col.insert_one({
                    "product_id": item, 
                    "product_category": product_info['product_category'],
                    "price": product_info['price'],
                    "historical_counts": [cur_counts_of_item]
                    })
            except Exception as e:
                print("Error:", e)
                return False
        else:
            try: 
                historical_counts_of_item['historical_counts'].append(cur_counts_of_item)
                item_count_col.update_one({"product_id": item},
                                        {'$set': historical_counts_of_item}
                                        )
            except Exception as e:
                print("Error:", e)
                return False
    return True

def check_surging_trend(item_count_col: pymongo.collection, item_counts_dict: dict, end_percentile: float , start_percentile: float = 0.1) -> list:
    surging_items = []
    for item in item_counts_dict:
        current_counts = item_counts_dict[item]
        historial_counts = item_count_col.find_one({"product_id": item})['historical_counts']
        if len(historial_counts) > 5:
            start_of_interval = np.percentile(historial_counts, start_percentile) # currently only use end_percentile to determine
            end_of_interval = np.percentile(historial_counts, end_percentile)
            # take the item if its count is higher than end-percentile 
            if current_counts >= end_of_interval: 
                surging_items.append(item)
    return surging_items

def update_trend_collection(surging_col: pymongo.collection, surging_items: list, item_count_col: pymongo.collection) -> True | False:
    # delete all first
    result = surging_col.delete_many({})
    for surging_item in surging_items:
        try:
            surging_col.insert_one(item_count_col.find_one({"product_id": surging_item}))
        except Exception as e:
                print("Error:", e)
                return False
    return True
            

# main function
def main():
    start_time = time.time()
    # running window
    QUERY_ORDERS = {"order_timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(**WINDOW)}}
    # start processing
    item_counts_dict = calculate_cur_item_counts(order_col = order_col, query = QUERY_ORDERS)
    execute_status = store_cur_item_counts(item_count_col, item_counts_dict)
    if execute_status: 
        surging_items = check_surging_trend(item_count_col, item_counts_dict, end_percentile = ANOMALY_THRESHOLD)
        if len(surging_items) > 0:
            execute_status = update_trend_collection(surging_col, surging_items, item_count_col)
            
    end_time = time.time()
    print("FINISH PROCESS: ", end_time - start_time)

# define scheduler logic
schedule.every(30).seconds.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
