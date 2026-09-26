import streamlit as st
import json
import os
import subprocess
import urllib.parse
import re
import time
import secrets


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-User F5-TTS Cloud Hub",
    page_icon="🎛️",
    layout="centered"
)


# ============================================================
# HELPERS
# ============================================================

def clean_slug(value: str) -> str:
    """
    Convert user input into a safe Kaggle kernel slug.
    """
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")

    if not value:
        value = "f5-tts-node"

    return value[:45]


def wait_for_port(host, port, timeout=360):
    """
    Wait until the remote F5-TTS process has opened port 7860.
    """
    import socket

    start_time = time.time()

    while time.time() - start_time < timeout:

        try:
            with socket.create_connection(
                (host, port),
                timeout=3
            ):
                return True

        except OSError:
            time.sleep(3)

    return False


def mask_secret(text, secret):
    """
    Prevent tokens from appearing in Streamlit error output.
    """
    if not text:
        return text

    if secret:
        text = text.replace(secret, "***HIDDEN***")

    return text


# ============================================================
# HEADER
# ============================================================

st.title("🎛️ Multi-User F5-TTS Cloud Hub")

st.write(
    "Apna Kaggle Token aur Ngrok Credentials dalein "
    "aur background mein Kaggle GPU par F5-TTS node start karein."
)


# ============================================================
# FORM
# ============================================================

with st.form("user_node_form"):

    st.subheader("1. Kaggle Authentication")

    kaggle_username = st.text_input(
        "Kaggle Username",
        placeholder="e.g. ahmadkhan"
    )

    kaggle_key = st.text_input(
        "Kaggle API Key",
        type="password",
        placeholder="Your Kaggle API token"
    )

    st.subheader("2. Ngrok Setup")

    ngrok_auth = st.text_input(
        "Ngrok Auth Token",
        type="password",
        placeholder="Your Ngrok Auth Token"
    )

    ngrok_domain = st.text_input(
        "Ngrok Static Domain",
        placeholder="your-domain.ngrok-free.app"
    )

    st.subheader("3. Node Settings")

    kernel_name = st.text_input(
        "Kaggle Node Name",
        value="F5 TTS Custom Node"
    )

    submit_btn = st.form_submit_button(
        "🚀 Deploy My Personal T4 Node",
        use_container_width=True
    )


# ============================================================
# WHATSAPP SUPPORT
# ============================================================

whatsapp_num = "923097647772"

raw_msg = (
    "Hello M Yousaf! I need guidance regarding "
    "the F5-TTS Voice Cloning setup. Kindly assist me."
)

encoded_msg = urllib.parse.quote(raw_msg)


# ============================================================
# DEPLOYMENT
# ============================================================

if submit_btn:

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not (
        kaggle_username
        and kaggle_key
        and ngrok_auth
        and ngrok_domain
    ):
        st.error(
            "Meharbani karke Kaggle Username, Kaggle API Key, "
            "Ngrok Auth Token aur Ngrok Domain sab fill karein."
        )

        st.stop()


    # --------------------------------------------------------
    # DOMAIN CLEANUP
    # --------------------------------------------------------

    ngrok_domain = ngrok_domain.strip()

    # Remove https:// if user pasted full URL
    ngrok_domain = re.sub(
        r"^https?://",
        "",
        ngrok_domain
    )

    ngrok_domain = ngrok_domain.rstrip("/")


    # --------------------------------------------------------
    # KERNEL SLUG
    # --------------------------------------------------------

    base_slug = clean_slug(kernel_name)

    random_suffix = secrets.token_hex(3)

    kernel_slug = f"{base_slug}-{random_suffix}"

    kernel_id = f"{kaggle_username}/{kernel_slug}"


    # --------------------------------------------------------
    # WORKING DIRECTORY
    # --------------------------------------------------------

    work_dir = os.path.abspath(
        f"f5tts_deploy_{random_suffix}"
    )

    os.makedirs(
        work_dir,
        exist_ok=True
    )


    # ========================================================
    # F5-TTS REMOTE APPLICATION
    # ========================================================

    wrapper_app_script = f'''
import os
import sys
import traceback

print("=" * 70)
print("F5-TTS REMOTE NODE STARTING")
print("=" * 70)

print("Python:", sys.version)

try:

    import torch

    print("PyTorch:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())

    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

except Exception as e:

    print("Torch check failed:")
    print(e)


# ------------------------------------------------------------
# IMPORT GRADIO
# ------------------------------------------------------------

try:

    import gradio as gr

    print("Gradio imported successfully.")

except Exception:

    traceback.print_exc()
    raise


# ------------------------------------------------------------
# IMPORT F5-TTS
# ------------------------------------------------------------

try:

    from f5_tts.infer.infer_gradio import app as f5_original_app

    print("F5-TTS application imported successfully.")

except Exception:

    print("=" * 70)
    print("F5-TTS IMPORT FAILED")
    print("=" * 70)

    traceback.print_exc()

    raise


# ------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------

custom_css = """
.gradio-container {{
    background-color: #111111 !important;
    color: #ffffff !important;
    font-family: Arial, sans-serif !important;
}}

footer {{
    display: none !important;
}}

#custom-brand {{
    margin-bottom: 20px;
}}
"""


# ------------------------------------------------------------
# CUSTOM BRANDING
# ------------------------------------------------------------

branding_html = """
<div id="custom-brand"
style="
background: linear-gradient(
    135deg,
    #667eea 0%,
    #764ba2 100%
);
padding: 25px;
border-radius: 15px;
color: white;
text-align: center;
margin-bottom: 20px;
box-shadow: 0 6px 25px rgba(0,0,0,0.35);
">

<h1 style="
margin:0;
font-size:30px;
font-weight:700;
">
Welcome to Advanced F5-TTS Portal
</h1>

<p style="
margin:8px 0 15px 0;
font-size:16px;
color:#e2e8f0;
">
F5-TTS Voice Cloning • GPU Powered
</p>

<hr style="
border:0;
border-top:1px solid rgba(255,255,255,0.25);
">

<p style="
margin:12px 0 8px 0;
font-weight:500;
">
🛠️ Designed & Optimized by <b>M Yousaf</b>
</p>

<a
href="https://wa.me{whatsapp_num}?text={encoded_msg}"
target="_blank"
style="
display:inline-block;
background:#25D366;
color:white;
padding:11px 22px;
border-radius:30px;
text-decoration:none;
font-weight:600;
font-size:14px;
margin-top:10px;
"
>
💬 Get Professional Guide & Support
</a>

</div>
"""


# ------------------------------------------------------------
# MASTER GRADIO APPLICATION
# ------------------------------------------------------------

try:

    with gr.Blocks(
        css=custom_css,
        title="F5-TTS Voice Portal | M Yousaf"
    ) as master_demo:

        gr.HTML(
            branding_html
        )

        gr.Markdown(
            """
            ## 🎙️ F5-TTS Voice Cloning

            Upload your reference audio, enter your text,
            and generate speech using the F5-TTS engine.
            """
        )

        # ----------------------------------------------------
        # ORIGINAL F5-TTS UI
        # ----------------------------------------------------

        f5_original_app.render()


    print("=" * 70)
    print("F5-TTS UI CREATED")
    print("=" * 70)


    # --------------------------------------------------------
    # LAUNCH
    # --------------------------------------------------------

    print("Starting Gradio server...")
    print("Host: 0.0.0.0")
    print("Port: 7860")

    master_demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        prevent_thread_lock=False
    )

except Exception:

    print("=" * 70)
    print("F5-TTS SERVER FAILED")
    print("=" * 70)

    traceback.print_exc()

    raise
'''


    # ========================================================
    # KAGGLE NOTEBOOK
    # ========================================================

    notebook_source = f'''
import os
import subprocess
import time
import socket
import sys


# ============================================================
# CONFIG
# ============================================================

NGROK_TOKEN = os.environ.get(
    "NGROK_AUTH_TOKEN",
    ""
)

NGROK_DOMAIN = "{ngrok_domain}"


# ============================================================
# BASIC SYSTEM CHECK
# ============================================================

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
    print("CUDA available:", torch.cuda.is_available())

    if torch.cuda.is_available():

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

    else:

        print(
            "WARNING: CUDA GPU is not available."
        )

except Exception as e:

    print(
        "Torch check error:",
        e
    )


# ============================================================
# INSTALL DEPENDENCIES
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
        "pyngrok",
        "f5-tts"
    ],
    check=True
)


# ============================================================
# KILL OLD SERVICES
# ============================================================

subprocess.run(
    "fuser -k 7860/tcp || true",
    shell=True
)

subprocess.run(
    "pkill -f master_wrapper_launcher.py || true",
    shell=True
)


# ============================================================
# WRITE F5-TTS APPLICATION
# ============================================================

wrapper_code = {wrapper_app_script!r}

with open(
    "master_wrapper_launcher.py",
    "w",
    encoding="utf-8"
) as f:

    f.write(wrapper_code)


# ============================================================
# START F5-TTS
# ============================================================

print("=" * 70)
print("STARTING F5-TTS SERVER")
print("=" * 70)

log_file = open(
    "f5tts_server.log",
    "w",
    buffering=1
)

process = subprocess.Popen(
    [
        sys.executable,
        "master_wrapper_launcher.py"
    ],
    stdout=log_file,
    stderr=subprocess.STDOUT,
    env=os.environ.copy()
)


# ============================================================
# WAIT FOR PORT 7860
# ============================================================

print(
    "Waiting for F5-TTS to open port 7860..."
)

server_ready = False

start_time = time.time()

while time.time() - start_time < 600:

    # Check if process already died
    if process.poll() is not None:

        print(
            "F5-TTS process exited."
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
            "F5-TTS server is READY!"
        )

        break

    except Exception:

        time.sleep(3)


# ============================================================
# SHOW LOG IF FAILED
# ============================================================

if not server_ready:

    print("=" * 70)
    print("F5-TTS FAILED TO START")
    print("=" * 70)

    try:

        log_file.flush()

        with open(
            "f5tts_server.log",
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            print(
                f.read()[-20000:]
            )

    except Exception as e:

        print(
            "Could not read log:",
            e
        )

    raise RuntimeError(
        "F5-TTS did not start on port 7860."
    )


# ============================================================
# NGROK
# ============================================================

print("=" * 70)
print("STARTING NGROK")
print("=" * 70)


from pyngrok import ngrok


if not NGROK_TOKEN:

    raise RuntimeError(
        "NGROK_AUTH_TOKEN is missing."
    )


ngrok.set_auth_token(
    NGROK_TOKEN
)


# Disconnect previous tunnels
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
# CONNECT STATIC DOMAIN
# ============================================================

try:

    tunnel = ngrok.connect(
        addr=7860,
        proto="http",
        hostname=NGROK_DOMAIN
    )

except Exception as e:

    print(
        "Ngrok static domain connection failed:"
    )

    print(e)

    print(
        "Trying normal ngrok URL..."
    )

    tunnel = ngrok.connect(
        addr=7860,
        proto="http"
    )


print("=" * 70)
print("F5-TTS NODE IS ONLINE")
print("=" * 70)

print(
    "PUBLIC URL:",
    tunnel.public_url
)

print("=" * 70)


# ============================================================
# KEEP KAGGLE KERNEL ALIVE
# ============================================================

while True:

    # If F5-TTS dies, show it
    if process.poll() is not None:

        print(
            "WARNING: F5-TTS process stopped."
        )

        break

    time.sleep(60)
'''


    # ========================================================
    # CREATE NOTEBOOK
    # ========================================================

    notebook_content = {

        "cells": [

            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import sys\n",
                    "\n",

                    # Ngrok token is passed through environment
                    f"os.environ['NGROK_AUTH_TOKEN'] = {ngrok_auth!r}\n",

                    notebook_source
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
        work_dir,
        "active_worker.ipynb"
    )


    with open(
        notebook_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            notebook_content,
            f,
            indent=2
        )


    # ========================================================
    # KAGGLE METADATA
    # ========================================================

    metadata = {

        "id": kernel_id,

        "title": kernel_name,

        "code_file": "active_worker.ipynb",

        "language": "python",

        "kernel_type": "notebook",

        "is_private": True,

        "enable_gpu": True,

        "enable_internet": True,

        "machine_shape": "NvidiaTeslaT4"
    }


    metadata_path = os.path.join(
        work_dir,
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
    # DEPLOY
    # ========================================================

    with st.status(
        "🚀 Deploying F5-TTS Kaggle GPU node...",
        expanded=True
    ):

        st.write(
            "📦 Preparing Kaggle notebook..."
        )

        st.write(
            "⚡ Requesting GPU environment..."
        )

        st.write(
            "🎙️ Preparing F5-TTS..."
        )

        st.write(
            "🌐 Preparing ngrok tunnel..."
        )


        try:

            # ------------------------------------------------
            # KAGGLE ENVIRONMENT
            # ------------------------------------------------

            env = os.environ.copy()

            env["KAGGLE_USERNAME"] = (
                kaggle_username
            )

            env["KAGGLE_API_TOKEN"] = (
                kaggle_key
            )


            # ------------------------------------------------
            # KAGGLE PUSH
            # ------------------------------------------------

            result = subprocess.run(

                [
                    "kaggle",
                    "kernels",
                    "push",
                    "-p",
                    work_dir
                ],

                capture_output=True,

                text=True,

                env=env,

                timeout=180
            )


            stdout = result.stdout or ""
            stderr = result.stderr or ""


            combined_output = (
                stdout + "\n" + stderr
            )


            # ------------------------------------------------
            # HIDE TOKENS
            # ------------------------------------------------

            combined_output = mask_secret(
                combined_output,
                kaggle_key
            )

            combined_output = mask_secret(
                combined_output,
                ngrok_auth
            )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if result.returncode == 0:

                st.success(
                    "🎉 Kaggle F5-TTS node successfully deployed!"
                )

                st.markdown(
                    f"""
                    ### 🔗 Your F5-TTS Web UI

                    **[Open F5-TTS Portal](https://{ngrok_domain})**

                    `https://{ngrok_domain}`
                    """
                )

                st.info(
                    "⏳ Agar page immediately open na ho, "
                    "30–90 seconds wait karke refresh karein. "
                    "F5-TTS model first startup par download/load hota hai."
                )


                with st.expander(
                    "Deployment Information"
                ):

                    st.code(
                        f"""
Kaggle Kernel:
{kernel_id}

GPU:
NvidiaTeslaT4

F5-TTS Port:
7860

Ngrok Domain:
https://{ngrok_domain}
"""
                    )


            else:

                st.error(
                    "❌ Kaggle deployment failed."
                )

                st.code(
                    combined_output[-12000:],
                    language="text"
                )

                st.markdown(
                    f"""
                    **Kaggle Kernel:**

                    `{kernel_id}`

                    Kaggle par is kernel ko open karke
                    **Logs / Output** check karein.
                    """
                )


        except subprocess.TimeoutExpired:

            st.error(
                "❌ Kaggle deployment command timed out."
            )

        except FileNotFoundError:

            st.error(
                "❌ Kaggle CLI installed nahi hai."
            )

            st.code(
                "pip install kaggle"
            )

        except Exception as e:

            safe_error = mask_secret(
                str(e),
                kaggle_key
            )

            safe_error = mask_secret(
                safe_error,
                ngrok_auth
            )

            st.error(
                f"❌ System Error: {safe_error}"
    )
