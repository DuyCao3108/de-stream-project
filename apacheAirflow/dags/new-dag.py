from airflow import DAG 
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.io.path import ObjectStoragePath

import boto3
import subprocess
import pandas as pd
import json

AWS_ACCESS_KEY = "AKIAVBC5LAOFFZNKBV7X"
AWS_SECRET_KEY = "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"
AWS_S3_BUCKET_NAME = "streaming-project-bucket"
AWS_S3_REGION_NAME = "ap-southeast-2"

AWS_CONN_ID = "aws-conn-new"
AWS_PREFIX = datetime.now().strftime("%Y-%m-%d")

AWS_STAGING_KEY = "staging/test.csv"

def get_object_task():
    s3_client = boto3.client(
        service_name = "s3",
        region_name = AWS_S3_REGION_NAME,
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_KEY
    )

    objects_list = s3_client.list_objects_v2(
        Bucket = AWS_S3_BUCKET_NAME,
        Prefix = AWS_PREFIX
    )['Contents']

    order_df = pd.DataFrame(columns=['order_id','customer_id','order_list_id','order_timestamp'])
    order_list_df = pd.DataFrame(columns=['order_list_id','product_id','quantity'])
    
    objects_list = [objects for objects in objects_list if objects['Size']!= 0]

    for object in objects_list:
        object_name = object['Key']
        obj = s3_client.get_object(Bucket = AWS_S3_BUCKET_NAME, Key=object_name)
        obj_data = obj['Body'].read()
        data = json.loads(obj_data.decode("utf-8"))
        
        order_key = data['order_timestamp']
        order_list = data['order_list']
        order_list_df_instance = pd.DataFrame(order_list)
        order_list_df_instance['order_list_id'] = order_key
    
        order_key = data['order_timestamp']
        order_df_instance = pd.DataFrame([{key: val for key, val in data.items() if key != "order_list"}])
        order_df_instance['order_id'] = order_key
        order_df_instance['order_list_id'] = order_key
    

        order_df = pd.concat([order_df, order_df_instance], ignore_index=True, axis= 0)
        order_list_df = pd.concat([order_list_df, order_list_df_instance], ignore_index=True, axis= 0)
    
    s3_client.put_object(
        Body = order_df.to_csv(index=0),
        Bucket = AWS_S3_BUCKET_NAME,
        Key = AWS_STAGING_KEY
    )


with DAG(
    "stream-dag",
    start_date = datetime(2024,4,26),
    schedule_interval = "@daily",
    catchup = False,
    tags=['duycao']
) as dag:
    
    hello_task = PythonOperator(
        task_id = "get-object",
        python_callable= get_object_task
    )