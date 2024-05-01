from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from kafka import KafkaProducer
import json

class OrderList(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    customer_id: int
    order_timestamp: datetime
    order_list: List[OrderList]

app = FastAPI()


@app.get("/")
def root():
    return {'message':'hello from the other side'}


@app.post("/order")
def create_order(item: Order):
    try:
        item.order_timestamp = datetime.now()
        json_as_string = json.dumps(jsonable_encoder(item))
        kafka_producer(json_as_string)
        return JSONResponse(content = jsonable_encoder(item), status_code = 201)
    except ValueError:
        return JSONResponse(content = jsonable_encoder(item), status_code=400)


def kafka_producer(json_as_string):
    producer = KafkaProducer(bootstrap_servers = "kafka:9092", acks = 1)
    producer.send("api-ingestion", bytes(json_as_string, "utf-8"))
    producer.flush() 


