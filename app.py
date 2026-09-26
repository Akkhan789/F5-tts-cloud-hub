import os
import sys
import time
import socket
import subprocess
import urllib.request

PORT = 7860

# Kill previous processes
subprocess.run(
    "fuser -k 7860/tcp || true",
    shell=True
)

# Install
subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-U",
        "f5-tts",
        "pyngrok"
    ],
    check=True
)

# Verify installation BEFORE starting server
subprocess.run(
    [
        sys.executable,
        "-c",
        "import f5_tts; print('F5-TTS import OK')"
    ],
    check=True
)

# Start official F5-TTS Gradio server
log_file = open("f5tts_server.log", "w")

server = subprocess.Popen(
    [
        "f5-tts_infer-gradio",
        "--host",
        "0.0.0.0",
        "--port",
        str(PORT)
    ],
    stdout=log_file,
    stderr=subprocess.STDOUT
)

print("F5-TTS process started:", server.pid)

# Wait until port is REALLY open
print("Waiting for F5-TTS server...")

ready = False

for i in range(180):
    time.sleep(2)

    if server.poll() is not None:
        print("❌ F5-TTS process crashed!")
        log_file.flush()

        with open("f5tts_server.log", "r") as f:
            print(f.read()[-12000:])

        raise RuntimeError("F5-TTS failed to start.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        sock.connect(("127.0.0.1", PORT))
        ready = True
        print("✅ Port 7860 is READY")
        sock.close()
        break
    except Exception:
        sock.close()

    if i % 5 == 0:
        print(f"Still waiting... {i * 2}s")

if not ready:
    print("❌ F5-TTS did not open port 7860.")

    log_file.flush()

    with open("f5tts_server.log", "r") as f:
        print(f.read()[-12000:])

    raise RuntimeError("F5-TTS server timeout.")

# Now ngrok
from pyngrok import ngrok

NGROK_TOKEN = "YOUR_TOKEN"
NGROK_DOMAIN = "YOUR_DOMAIN"

ngrok.set_auth_token(NGROK_TOKEN)

tunnel = ngrok.connect(
    addr="127.0.0.1:7860",
    proto="http",
    hostname=NGROK_DOMAIN
)

print("================================")
print("✅ F5-TTS IS LIVE")
print("🌐 URL:", tunnel.public_url)
print("================================")

# Keep notebook alive
while True:
    time.sleep(60)
