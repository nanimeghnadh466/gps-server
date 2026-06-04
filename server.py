# """
# server.py — HTTP receiver for nRF9151 GPS telemetry
 
# Run:
#     python server.py
 
# Listens on:
#     [::]:5000 (IPv6 + IPv4)
 
# Endpoints:
#     POST /        GPS fix or status
#     POST /gps     GPS fix JSON
#     POST /status  No-fix status JSON
# """
 
# from flask import Flask, request
# from datetime import datetime
 
# app = Flask(__name__)
 
# def log_request(path, data):
#     ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
 
#     print("\n" + "=" * 60)
#     print(f"[{ts}] POST {path}")
#     print(f"From : {request.remote_addr}")
#     print(f"Body : {data}")
#     print("=" * 60)
 
# @app.route("/", methods=["POST"])
# def root():
#     data = request.get_data(as_text=True)
 
#     print("Hi")
#     log_request("/", data)
 
#     return "Hi", 200
 
# @app.route("/gps", methods=["POST"])
# def gps():
#     data = request.get_data(as_text=True)
 
#     print("Hi")
#     log_request("/gps", data)
 
#     return "Hi", 200
 
# @app.route("/status", methods=["POST"])
# def status():
#     data = request.get_data(as_text=True)
 
#     print("Hi")
#     log_request("/status", data)
 
#     return "Hi", 200
 
# if __name__ == "__main__":
#     print("=" * 60)
#     print("nRF9151 GPS Receiver")
#     print("Listening on [::]:5000 (IPv6 + IPv4)")
#     print("=" * 60)
 
#     app.run(
#         host="::",
#         port=5000,
#         debug=False
#     )

"""
server.py — nRF9151 GPS Telemetry Server
Deploy on Render.com for a permanent free URL.

Endpoints:
    POST /        GPS fix or status (firmware uses / for both)
    POST /gps     GPS fix JSON
    POST /status  No-fix status JSON
    GET  /        View last 20 GPS fixes (auto-refreshes)
    GET  /status  View last 10 status records
"""

import os
import json
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# In-memory storage (last 100 records)
gps_records    = []
status_records = []

# ── Helpers ───────────────────────────────────────────────────

def log_request(path, data):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print("\n" + "=" * 60)
    print(f"[{ts}] POST {path}")
    print(f"  From : {request.remote_addr}")
    print(f"  Body : {data}")
    print("=" * 60)

def html_table(records, title, refresh=10):
    if not records:
        rows    = "<tr><td colspan='99'>No data yet</td></tr>"
        headers = ""
    else:
        headers = "".join(f"<th>{k}</th>" for k in records[-1].keys())
        rows    = ""
        for r in reversed(records[-20:]):
            rows += "<tr>" + "".join(f"<td>{v}</td>" for v in r.values()) + "</tr>"

    return f"""<!DOCTYPE html>
<html>
<head>
  <title>{title}</title>
  <meta http-equiv="refresh" content="{refresh}">
  <style>
    body  {{ font-family: monospace; background: #111; color: #0f0; padding: 20px; }}
    h2    {{ color: #0f0; }}
    p     {{ color: #888; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td{{ border: 1px solid #333; padding: 6px 12px; text-align: left; }}
    th    {{ background: #1a1a1a; color: #0ff; }}
    tr:hover{{ background: #1a1a1a; }}
    a     {{ color: #0ff; }}
  </style>
</head>
<body>
  <h2>📡 {title}</h2>
  <p>
    Records: {len(records)} |
    Auto-refresh every {refresh}s |
    <a href="/">GPS Fixes</a> |
    <a href="/status">Status</a>
  </p>
  <table>
    <thead><tr>{headers}</tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""

# ── Routes ────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        data = request.get_data(as_text=True)
        log_request("/", data)

        try:
            parsed = json.loads(data)
            parsed["server_time"] = datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC")

            # Route to correct bucket based on content
            if "lat" in parsed:
                gps_records.append(parsed)
                if len(gps_records) > 100:
                    gps_records.pop(0)
            else:
                status_records.append(parsed)
                if len(status_records) > 50:
                    status_records.pop(0)
        except Exception as e:
            print(f"JSON parse error: {e}")

        return "OK", 200

    # GET — show GPS table
    return html_table(gps_records, "nRF9151 GPS Fixes"), 200


@app.route("/gps", methods=["GET", "POST"])
def gps():
    if request.method == "POST":
        data = request.get_data(as_text=True)
        log_request("/gps", data)

        try:
            parsed = json.loads(data)
            parsed["server_time"] = datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC")
            gps_records.append(parsed)
            if len(gps_records) > 100:
                gps_records.pop(0)
        except Exception as e:
            print(f"JSON parse error: {e}")

        return "OK", 200

    return html_table(gps_records, "nRF9151 GPS Fixes"), 200


@app.route("/status", methods=["GET", "POST"])
def status():
    if request.method == "POST":
        data = request.get_data(as_text=True)
        log_request("/status", data)

        try:
            parsed = json.loads(data)
            parsed["server_time"] = datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC")
            status_records.append(parsed)
            if len(status_records) > 50:
                status_records.pop(0)
        except Exception as e:
            print(f"JSON parse error: {e}")

        return "OK", 200

    return html_table(status_records, "nRF9151 Device Status"), 200


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("=" * 60)
    print("  nRF9151 GPS Telemetry Server")
    print(f"  Listening on 0.0.0.0:{port}")
    print("  Endpoints: /  /gps  /status")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )