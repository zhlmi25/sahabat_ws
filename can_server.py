import time

from gs_usb.gs_usb import GsUsb
from gs_usb.gs_usb_frame import GsUsbFrame
from gs_usb.constants import (
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
)

from functools import cached_property, lru_cache
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import json

devs = GsUsb.scan()
if len(devs) == 0:
    raise RuntimeError("Can not find gs_usb device")
dev = devs[0]
if not dev.set_bitrate(500000):
    raise RuntimeError("Can not set bitrate for gs_usb")
dev.start()


class WebRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length)

    @cached_property
    def form_data(self):
        return dict(parse_qsl(self.post_data.decode("utf-8")))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def do_GET(self):
        global dev
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        iframe = GsUsbFrame()
        result = {}
        for _ in range(100):
            if dev.read(iframe, 1):
                result = {
                    "can_id": iframe.can_id,
                    "data": list(iframe.data),
                    "flags": {
                        "EFF": bool(iframe.can_id & CAN_EFF_FLAG),
                        "RTR": bool(iframe.can_id & CAN_RTR_FLAG),
                        "ERR": bool(iframe.can_id & CAN_ERR_FLAG),
                    }
                }
                break
        else:
            result = {"error": "No CAN frame received"}
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def do_POST(self):
        global dev
        try:
            data = json.loads(self.post_data.decode("utf-8"))
            can_id = int(data.get("can_id"))
            can_data = bytes(data.get("data"))
            frame = GsUsbFrame(can_id=can_id, data=can_data)
            while True:
                sent = dev.send(frame)
                iframe = GsUsbFrame()
                if dev.read(iframe, 1):
                    if iframe.can_id == can_id:
                        break
            response = {"status": "sent" if sent else "failed",
                        "can_id": can_id, "data": list(can_data)}
        except Exception as e:
            response = {"error": str(e)}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))


def main():
    # Find our device
    devs = GsUsb.scan()
    if len(devs) == 0:
        print("Can not find gs_usb device")
        return
    dev = devs[0]

    # Configuration
    if not dev.set_bitrate(500000):
        print("Can not set bitrate for gs_usb")
        return

    # Start device
    dev.start()

    rpm = 1000
    left_id = 15
    RPM_FLAG = 0x300

    # Prepare frames
    data = rpm.to_bytes(4, byteorder='little')
    rtr_with_data_frame = GsUsbFrame(
        can_id=left_id | RPM_FLAG | CAN_EFF_FLAG, data=data)
    frames = [
        rtr_with_data_frame,
    ]

    # Read all the time and send message in each second
    end_time, n = time.time() + 1, -1
    while True:
        iframe = GsUsbFrame()
        if dev.read(iframe, 1):
            ...
            print("RX  {}".format(iframe))

        if time.time() - end_time >= 0:
            end_time = time.time() + 1
            n += 1
            n %= len(frames)

            if dev.send(frames[n]):
                print("TX  {}".format(frames[n]))


if __name__ == "__main__":
    try:
        server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
