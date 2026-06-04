""" server.py — HTTP receiver for nRF9151 GPS telemetry
Run:     python server.py
Listens on:     [::]:5000 (IPv6 + IPv4)
Endpoints:     POST /        GPS fix or status     POST /gps     GPS fix JSON     POST /status  No-fix status JSON """
from flask import Flask, request
from datetime import datetime
import os
app = Flask(__name__)
def log_request(path, data):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print("\n" + "=" * 60)
    print(f"[{ts}] POST {path}")
    print(f"From : {request.remote_addr}")
    print(f"Body : {data}")
    print("=" * 60)
@app.route("/", methods=["POST"])
def root():
    data = request.get_data(as_text=True)
    print("Hi")
    log_request("/", data)
    return "Hi", 200
@app.route("/gps", methods=["POST"])
def gps():
    data = request.get_data(as_text=True)
    print("Hi")
    log_request("/gps", data)
    return "Hi", 200
@app.route("/status", methods=["POST"])
def status():
    data = request.get_data(as_text=True)
    print("Hi")
    log_request("/status", data)
    return "Hi", 200
if __name__ == "__main__":
    print("=" * 60)
    print("nRF9151 GPS Receiver")
    print("Listening on [::]:5000 (IPv6 + IPv4)")
    print("=" * 60)
    port = int(os.environ.get("PORT", 5000))   # ← Railway needs this
    app.run(
        host="0.0.0.0",                        # ← Railway needs this
        port=port,                             # ← Railway needs this
        debug=False
    )