import os
import socket
import subprocess
import sys
import time
import urllib.request

NGROK_TOKEN = __NGROK_TOKEN__
NGROK_DOMAIN = __NGROK_DOMAIN__
F5_VERSION = "1.1.22"


def wait_for_http(url: str, timeout: int = 900):
    started = time.time()
    last_error = ""
    while time.time() - started < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "F5-TTS-Health"})
            with urllib.request.urlopen(req, timeout=5) as response:
                if 200 <= response.status < 500:
                    return True
        except Exception as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"F5-TTS HTTP service did not become ready: {last_error}")


def main():
    print("F5-TTS node starting")

    # Keep the node focused on one service.
    subprocess.run(
        "fuser -k 7860/tcp || true",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("Installing F5-TTS...")
    install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--no-cache-dir",
            f"f5-tts=={F5_VERSION}",
            "ngrok",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if install.returncode != 0:
        print(install.stdout[-12000:])
        raise RuntimeError("F5-TTS installation failed")

    gpu = subprocess.run(
        [
            sys.executable,
            "-c",
            "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO GPU')",
        ],
        capture_output=True,
        text=True,
    )
    print("GPU:", gpu.stdout.strip().replace("\n", " | "))
    if gpu.returncode != 0 or not gpu.stdout.splitlines() or gpu.stdout.splitlines()[0].strip().lower() != "true":
        raise RuntimeError("Kaggle GPU is not available")

    print("Starting F5-TTS on port 7860...")
    server = subprocess.Popen(
        [
            "f5-tts_infer-gradio",
            "--port",
            "7860",
            "--host",
            "0.0.0.0",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    try:
        wait_for_http("http://127.0.0.1:7860/", timeout=900)
        print("F5-TTS HTTP service is ready")

        import ngrok

        forwarder = ngrok.forward(
            "http://127.0.0.1:7860",
            authtoken=NGROK_TOKEN,
            domain=NGROK_DOMAIN,
        )
        print("F5-TTS public URL:", forwarder.url())
        print("F5-TTS node is ready")

        while True:
            if server.poll() is not None:
                raise RuntimeError("F5-TTS process stopped")
            time.sleep(30)
    finally:
        if server.poll() is None:
            server.terminate()


if __name__ == "__main__":
    main()
