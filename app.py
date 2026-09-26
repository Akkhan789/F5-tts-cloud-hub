import streamlit as st
import os
import json
import subprocess
import urllib.parse
import re
import secrets
import time


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="F5-TTS Cloud Hub",
    page_icon="🎙️",
    layout="centered"
)


# ============================================================
# HELPERS
# ============================================================

def clean_slug(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")

    if not text:
        text = "f5-tts-node"

    return text[:40]


def hide_secret(text, secret):
    if not text:
        return text

    if secret:
        return text.replace(secret, "***HIDDEN***")

    return text


# ============================================================
# HEADER
# ============================================================

st.title("🎙️ Multi-User F5-TTS Cloud Hub")

st.write(
    "Kaggle T4 GPU par F5-TTS Voice Cloning node deploy karein "
    "aur apne Ngrok static domain ke through access karein."
)


# ============================================================
# FORM
# ============================================================

with st.form("deployment_form"):

    st.subheader("🔐 Kaggle")

    kaggle_username = st.text_input(
        "Kaggle Username",
        placeholder="your-kaggle-username"
    )

    kaggle_key = st.text_input(
        "Kaggle API Token",
        type="password",
        placeholder="Kaggle API token"
    )

    st.subheader("🌐 Ngrok")

    ngrok_auth = st.text_input(
        "Ngrok Auth Token",
        type="password",
        placeholder="Ngrok auth token"
    )

    ngrok_domain = st.text_input(
        "Ngrok Static Domain",
        placeholder="eggplant-mushily-guiding.ngrok-free.dev"
    )

    st.subheader("⚙️ Node")

    node_name = st.text_input(
        "Node Name",
        value="F5 TTS Cloud Node"
    )

    deploy = st.form_submit_button(
        "🚀 Deploy T4 F5-TTS Node",
        use_container_width=True
    )


# ============================================================
# SUPPORT
# ============================================================

whatsapp_num = "923097647772"

message = urllib.parse.quote(
    "Hello M Yousaf! I need guidance regarding the F5-TTS Voice Cloning setup."
)


# ============================================================
# DEPLOY
# ============================================================

if deploy:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not all([
        kaggle_username,
        kaggle_key,
        ngrok_auth,
        ngrok_domain
    ]):

        st.error(
            "Kaggle Username, Kaggle Token, Ngrok Token "
            "aur Ngrok Domain sab required hain."
        )

        st.stop()


    # --------------------------------------------------------
    # CLEAN DOMAIN
    # --------------------------------------------------------

    ngrok_domain = ngrok_domain.strip()

    ngrok_domain = re.sub(
        r"^https?://",
        "",
        ngrok_domain
    )

    ngrok_domain = ngrok_domain.rstrip("/")


    # --------------------------------------------------------
    # UNIQUE KERNEL
    # --------------------------------------------------------

    suffix = secrets.token_hex(3)

    slug = clean_slug(node_name)

    kernel_slug = f"{slug}-{suffix}"

    kernel_id = f"{kaggle_username}/{kernel_slug}"


    # --------------------------------------------------------
    # DEPLOY DIRECTORY
    # --------------------------------------------------------

    deploy_dir = os.path.abspath(
        f"f5tts_{suffix}"
    )

    os.makedirs(
        deploy_dir,
        exist_ok=True
    )


    # ========================================================
    # KAGGLE NOTEBOOK
    # ========================================================

    notebook_code = r'''
import os
import sys
import subprocess
import time
import socket
import traceback


# ============================================================
# CONFIG
# ============================================================

NGROK_TOKEN = os.environ.get(
    "NGROK_AUTH_TOKEN",
    ""
)

NGROK_DOMAIN = os.environ.get(
    "NGROK_DOMAIN",
    ""
)


print("=" * 70)
print("F5-TTS KAGGLE NODE")
print("=" * 70)

print("Python:", sys.version)


# ============================================================
# GPU CHECK
# ============================================================

try:

    import torch

    print("PyTorch:", torch.__version__)
    print(
        "CUDA available:",
        torch.cuda.is_available()
    )

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

except Exception as e:

    print("GPU check error:", e)


# ============================================================
# INSTALL
# ============================================================

print("=" * 70)
print("INSTALLING F5-TTS")
print("=" * 70)

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


# ============================================================
# CLEAN PORT
# ============================================================

print("Cleaning port 7860...")

subprocess.run(
    "fuser -k 7860/tcp || true",
    shell=True
)


# ============================================================
# START OFFICIAL F5-TTS SERVER
# ============================================================

print("=" * 70)
print("STARTING OFFICIAL F5-TTS GRADIO SERVER")
print("=" * 70)

log_path = "f5tts.log"

log_file = open(
    log_path,
    "w",
    buffering=1
)


f5_process = subprocess.Popen(
    [
        "f5-tts_infer-gradio",
        "--host",
        "0.0.0.0",
        "--port",
        "7860"
    ],
    stdout=log_file,
    stderr=subprocess.STDOUT,
    env=os.environ.copy()
)


# ============================================================
# WAIT FOR F5-TTS
# ============================================================

print(
    "Waiting for F5-TTS server..."
)

server_ready = False

start_time = time.time()

while time.time() - start_time < 600:

    # Process crashed?
    if f5_process.poll() is not None:

        print(
            "ERROR: F5-TTS process stopped."
        )

        break

    try:

        sock = socket.create_connection(
            ("127.0.0.1", 7860),
            timeout=3
        )

        sock.close()

        server_ready = True

        print(
            "F5-TTS SERVER READY ON PORT 7860"
        )

        break

    except Exception:

        time.sleep(3)


# ============================================================
# FAILED
# ============================================================

if not server_ready:

    print("=" * 70)
    print("F5-TTS FAILED TO START")
    print("=" * 70)

    try:

        log_file.flush()

        with open(
            log_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            print(
                f.read()[-30000:]
            )

    except Exception as e:

        print(
            "Unable to read F5-TTS log:",
            e
        )

    raise RuntimeError(
        "F5-TTS did not open port 7860."
    )


# ============================================================
# NGROK
# ============================================================

print("=" * 70)
print("STARTING NGROK")
print("=" * 70)


if not NGROK_TOKEN:

    raise RuntimeError(
        "NGROK_AUTH_TOKEN is missing."
    )


if not NGROK_DOMAIN:

    raise RuntimeError(
        "NGROK_DOMAIN is missing."
    )


from pyngrok import ngrok


# ------------------------------------------------------------
# AUTH
# ------------------------------------------------------------

ngrok.set_auth_token(
    NGROK_TOKEN
)


# ------------------------------------------------------------
# REMOVE OLD TUNNELS
# ------------------------------------------------------------

try:

    tunnels = ngrok.get_tunnels()

    for tunnel in tunnels:

        try:

            ngrok.disconnect(
                tunnel.public_url
            )

        except Exception:

            pass

except Exception:

    pass


# ============================================================
# CREATE STATIC DOMAIN TUNNEL
# ============================================================

print(
    "Connecting static domain:",
    NGROK_DOMAIN
)


try:

    tunnel = ngrok.connect(
        addr=7860,
        proto="http",
        hostname=NGROK_DOMAIN
    )

except Exception as e:

    print("=" * 70)
    print("STATIC NGROK DOMAIN FAILED")
    print("=" * 70)

    print(e)

    raise


# ============================================================
# SUCCESS
# ============================================================

print("=" * 70)
print("============================================")
print("F5-TTS NODE ONLINE")
print("============================================")
print("PUBLIC URL:")
print(tunnel.public_url)
print("============================================")
print("=" * 70)


# ============================================================
# KEEP ALIVE
# ============================================================

while True:

    if f5_process.poll() is not None:

        print(
            "WARNING: F5-TTS process stopped."
        )

        break

    time.sleep(30)
'''


    # ========================================================
    # ENVIRONMENT SETUP CELL
    # ========================================================

    first_cell = f'''
import os

os.environ["NGROK_AUTH_TOKEN"] = {ngrok_auth!r}

os.environ["NGROK_DOMAIN"] = {ngrok_domain!r}

exec({notebook_code!r})
'''


    # ========================================================
    # NOTEBOOK
    # ========================================================

    notebook = {

        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    line + "\n"
                    for line in first_cell.splitlines()
                ]
            }
        ],

        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },

            "language_info": {
                "name": "python"
            }
        },

        "nbformat": 4,
        "nbformat_minor": 5
    }


    notebook_path = os.path.join(
        deploy_dir,
        "active_worker.ipynb"
    )


    with open(
        notebook_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            notebook,
            f,
            indent=2
        )


    # ========================================================
    # KAGGLE METADATA
    # ========================================================

    metadata = {

        "id": kernel_id,

        "title": node_name,

        "code_file": "active_worker.ipynb",

        "language": "python",

        "kernel_type": "notebook",

        "is_private": True,

        "enable_gpu": True,

        "enable_internet": True,

        "machine_shape": "NvidiaTeslaT4"
    }


    metadata_path = os.path.join(
        deploy_dir,
        "kernel-metadata.json"
    )


    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2
        )


    # ========================================================
    # DEPLOY STATUS
    # ========================================================

    with st.status(
        "🚀 Deploying F5-TTS...",
        expanded=True
    ):

        st.write(
            "📦 Kaggle notebook prepared"
        )

        st.write(
            "⚡ T4 GPU requested"
        )

        st.write(
            "🎙️ F5-TTS server configured"
        )

        st.write(
            "🌐 Ngrok static domain configured"
        )


        # ====================================================
        # KAGGLE ENVIRONMENT
        # ====================================================

        env = os.environ.copy()

        env["KAGGLE_USERNAME"] = (
            kaggle_username
        )

        env["KAGGLE_API_TOKEN"] = (
            kaggle_key
        )


        # ====================================================
        # KAGGLE PUSH
        # ====================================================

        try:

            result = subprocess.run(

                [
                    "kaggle",
                    "kernels",
                    "push",
                    "-p",
                    deploy_dir,
                    "--accelerator",
                    "NvidiaTeslaT4"
                ],

                capture_output=True,

                text=True,

                env=env,

                timeout=180
            )


        except FileNotFoundError:

            st.error(
                "Kaggle CLI installed nahi hai."
            )

            st.code(
                "pip install kaggle"
            )

            st.stop()


        except subprocess.TimeoutExpired:

            st.error(
                "Kaggle deployment timeout ho gaya."
            )

            st.stop()


        # ====================================================
        # OUTPUT
        # ====================================================

        stdout = result.stdout or ""

        stderr = result.stderr or ""

        output = (
            stdout +
            "\n" +
            stderr
        )


        output = hide_secret(
            output,
            kaggle_key
        )

        output = hide_secret(
            output,
            ngrok_auth
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        if result.returncode == 0:

            st.success(
                "✅ Kaggle T4 node successfully submitted!"
            )

            st.markdown(
                f"""
### 🎙️ Your F5-TTS Portal

**[OPEN F5-TTS](https://{ngrok_domain})**

`https://{ngrok_domain}`
"""
            )

            st.info(
                "Kaggle ko F5-TTS start karne mein kuch minutes "
                "lag sakte hain. Agar page abhi offline ho to "
                "Kaggle kernel status/logs mein RUNNING check karein."
            )


            st.code(
                f"""
Kaggle Kernel:
{kernel_id}

GPU:
NvidiaTeslaT4

F5-TTS:
Port 7860

Ngrok:
https://{ngrok_domain}
"""
            )


            with st.expander(
                "Kaggle CLI Output"
            ):

                st.code(
                    output[-10000:],
                    language="text"
                )


        else:

            st.error(
                "❌ Kaggle kernel deploy nahi hua."
            )

            st.code(
                output[-15000:],
                language="text"
    )
