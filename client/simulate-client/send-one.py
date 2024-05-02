import requests
from datetime import datetime, timezone

url = "http://localhost:80/order/"

payload = {
    "customer_id": 1,
    "order_list": [
        {
            "product_id": 1,
            "quantity": 2
        },
        {
            "product_id": 2,
            "quantity": 3
        }
    ],
    "order_timestamp": str(datetime.now())
}
headers = {
    "Content-Type": "application/json",
    "User-Agent": "insomnia/8.6.1"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(str(datetime.now(timezone.utc)))
print(response.text)