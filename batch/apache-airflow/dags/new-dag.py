from airflow import DAG 
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.io.path import ObjectStoragePath
import boto3
import subprocess
import pandas as pd
import json
import psycopg2

AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_S3_BUCKET_NAME = "streaming-project-bucket"
AWS_S3_REGION_NAME = "ap-southeast-2"

AWS_CONN_ID = "aws-conn-new"
AWS_PREFIX = datetime.now().strftime("%Y-%m-%d")

AWS_STAGING_KEY_ORDER = "staging/staging_order/test.csv"
AWS_STAGING_KEY_ORDER_LIST = "staging/staging_order_list/test.csv"
AWS_STAGING_KEY_CUSTOMER = "staging/staging_customer/test.csv"
AWS_STAGING_KEY_PRODUCT = "staging/staging_product/test.csv"

# postgres connection parameter
HOST = ""
DATABASE = "postgres"
USER = "postgres"
PASSWORD = "example"


def helper_connect_s3(AWS_S3_REGION_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY):
    s3_client = boto3.client(
        service_name = "s3",
        region_name = AWS_S3_REGION_NAME,
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_KEY
    )
    return s3_client 

def helper_connect_postgres(HOST, DATABASE, USER, PASSWORD):
    pg_conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD
    )
    return pg_conn

def transfer_order_data():
    s3_client = helper_connect_s3(AWS_S3_REGION_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY)

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
        Key = AWS_STAGING_KEY_ORDER
    )

    s3_client.put_object(
        Body = order_list_df.to_csv(index=0),
        Bucket = AWS_S3_BUCKET_NAME,
        Key = AWS_STAGING_KEY_ORDER_LIST
    )

def transfer_customer_data():
    # connect
    s3_client = helper_connect_s3(AWS_S3_REGION_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    pg_conn = helper_connect_postgres(HOST, DATABASE, USER, PASSWORD)
    # query data
    cur = pg_conn.cursor()
    cur.execute("SELECT * FROM public.customer")
    col_names = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=col_names)
    # upload s3
    s3_client.put_object(
        Body = df.to_csv(index=0),
        Bucket = AWS_S3_BUCKET_NAME,
        Key = AWS_STAGING_KEY_CUSTOMER
    )

def transfer_product_data():
    # connect
    s3_client = helper_connect_s3(AWS_S3_REGION_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    pg_conn = helper_connect_postgres(HOST, DATABASE, USER, PASSWORD)
    # query data
    cur = pg_conn.cursor()
    cur.execute("SELECT * FROM public.product")
    col_names = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=col_names)
    # upload s3
    s3_client.put_object(
        Body = df.to_csv(index=0),
        Bucket = AWS_S3_BUCKET_NAME,
        Key = AWS_STAGING_KEY_PRODUCT
    )



with DAG(
    "s3-data-transfer",
    start_date = datetime(2024,4,26),
    schedule_interval = "@daily",
    catchup = False,
    tags=['duycao']
) as dag:
    
    transfer_order_task = PythonOperator(
        task_id = "transfer-order",
        python_callable= transfer_order_data
    )

    transfer_customer_task = PythonOperator(
        task_id = "transfer-customer",
        python_callable= transfer_customer_data
    )

    transfer_product_task = PythonOperator(
        task_id = "transfer-product",
        python_callable= transfer_product_data
    )