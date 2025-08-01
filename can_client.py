import requests
from gs_usb.constants import (
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
)
# Prepare CAN ID and data
can_id = 15 | 0x300 | CAN_EFF_FLAG  # left_id | RPM_FLAG | CAN_EFF_FLAG
rpm = 1000
data_bytes = list(rpm.to_bytes(4, byteorder='little'))

payload = {
    "can_id": can_id,
    "data": data_bytes
}

for _ in range(1):
    response = requests.post("http://localhost:8000", json=payload)
    # response = requests.get("http://localhost:8000")
    print(response.json())