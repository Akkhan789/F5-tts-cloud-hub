import streamlit as st
import json
import os
import subprocess
import urllib.parse

st.set_page_config(page_title="Multi-User F5-TTS Core Hub", page_icon="🎛️", layout="centered")

st.title("🎛️ Multi-User F5-TTS Cloud Hub")
st.write("Apna Kaggle Token aur Ngrok Credentials dalein aur background mein free T4 GPU par F5-TTS node start karein.")

with st.form("user_node_form"):
    st.subheader("1. Kaggle Authentication")
    kaggle_username = st.text_input("Kaggle Username", placeholder="e.g., ahmadkhan")
    kaggle_key = st.text_input("Kaggle API Key", type="password", placeholder="Kaggle API token")

    st.subheader("2. Ngrok Multi-Tunnel Setup")
    ngrok_auth = st.text_input("Ngrok Auth Token", type="password", placeholder="Ngrok auth token")
    ngrok_domain = st.text_input("Ngrok Static Domain (Unique per user)", placeholder="e.g., your-unique-id.ngrok-free.app")
    submit_btn = st.form_submit_button("🚀 Deploy My Personal T4 Node")

whatsapp_num = "923097647772"
raw_msg = "Hello M Yousaf! I need guidance regarding the F5-TTS Voice Cloning setup. Kindly assist me."
encoded_msg = urllib.parse.quote(raw_msg)

if submit_btn:
    if not all([kaggle_username, kaggle_key, ngrok_auth, ngrok_domain]):
        st.error("Meharbani karke saari fields fill karein!")
    else:
        with st.spinner("Kaggle notebook prepare ho rahi hai aur T4 node deploy ho raha hai..."):
            try:
                os.environ["KAGGLE_USERNAME"] = kaggle_username
                os.environ["KAGGLE_API_TOKEN"] = kaggle_key

                # The wrapper deliberately imports F5-TTS only inside the Kaggle
                # process. This prevents the Streamlit host from trying to import it.
                wrapper_app_script = '''
import time
import traceback

print("=" * 70)
print("F5-TTS WRAPPER: IMPORT STAGE")
print("=" * 70)

try:
    import gradio as gr
    print("OK: Gradio imported")
    print("Gradio version:", getattr(gr, "__version__", "unknown"))

    print("Loading F5-TTS infer_gradio...")
    from f5_tts.infer.infer_gradio import app as f5_original_app

    print("OK: F5-TTS infer_gradio imported")
    print("OK: F5-TTS application object loaded")

except Exception as e:
    print("=" * 70)
    print("F5-TTS IMPORT / INITIALIZATION FAILED")
    print("=" * 70)
    print("ERROR:", repr(e))
    traceback.print_exc()
    print("=" * 70)
    raise

custom_css = """
.gradio-container {
    background-color: #111111 !important;
    color: #ffffff !important;
    font-family: 'Poppins', sans-serif !important;
}
body {
    background-color: #111111 !important;
}
"""

branding_html = """
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:25px;border-radius:12px;color:white;text-align:center;margin-bottom:25px;box-shadow:0 4px 15px rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.1);">
<h1 style="margin:0;font-size:28px;font-weight:700;color:white;">Welcome to Advanced F5-TTS Portal</h1>
<p style="margin:5px 0 15px;font-size:16px;color:#e2e8f0;">Dynamic Multi-User Infrastructure Enabled</p>
<hr style="border:0;border-top:1px solid rgba(255,255,255,.2);margin:10px 0;">
<p style="margin:5px 0;font-weight:500;font-size:15px;color:#f7fafc;">🛠️ Build, Designed &amp; Optimized by <b>M Yousaf</b></p>
<a href="https://wa.me/WHATSAPP_NUMBER?text=WHATSAPP_MESSAGE" target="_blank" style="display:inline-flex;align-items:center;background:#25D366;color:white;padding:10px 20px;border-radius:30px;text-decoration:none;font-weight:600;font-size:14px;margin-top:12px;">Get Professional Guide &amp; Support</a>
</div>
"""

branding_html = branding_html.replace("WHATSAPP_NUMBER", "923097647772").replace("WHATSAPP_MESSAGE", "Hello%20M%20Yousaf%21%20I%20need%20guidance%20regarding%20the%20F5-TTS%20Voice%20Cloning%20setup.%20Kindly%20assist%20me.")

with gr.Blocks(css=custom_css, title="F5-TTS Voice Portal | M Yousaf") as master_demo:
    gr.HTML(branding_html)
    with gr.Row():
        file_title = gr.Textbox(label="💾 Set Output Audio Download Name (Optional)", placeholder="e.g., Cloned_Speech_Yousaf_Project")
    with gr.Row():
        f5_original_app.render()

print("F5-TTS UI BUILD SUCCESS")
print("Starting Gradio on 0.0.0.0:7860")

master_demo.queue().launch(server_name="0.0.0.0", server_port=7860, show_error=True)
'''

                notebook_source = r'''
import os
import sys
import time
import socket
import subprocess

print("=" * 70)
print("F5-TTS KAGGLE NODE BOOT")
print("=" * 70)

NGROK_TOKEN = __NGROK_TOKEN__
NGROK_DOMAIN = __NGROK_DOMAIN__

# ------------------------------------------------------------
# Clean only the target service port.
# ------------------------------------------------------------
subprocess.run("fuser -k 7860/tcp || true", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ------------------------------------------------------------
# STAGE 1 - INSTALL
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 1: INSTALLING F5-TTS + PYNGROK")
print("=" * 70)

install_result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-U", "f5-tts", "pyngrok"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
print(install_result.stdout[-25000:])
if install_result.returncode != 0:
    raise RuntimeError("F5-TTS PIP INSTALL FAILED")
print("STAGE 1 PASSED")

# ------------------------------------------------------------
# STAGE 2 - PYTORCH / CUDA
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 2: PYTORCH / CUDA CHECK")
print("=" * 70)

cuda_result = subprocess.run(
    [sys.executable, "-c", "import torch; print('TORCH_VERSION:', torch.__version__); print('CUDA_AVAILABLE:', torch.cuda.is_available()); print('TORCH_CUDA_VERSION:', torch.version.cuda); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
print(cuda_result.stdout)
if cuda_result.returncode != 0:
    raise RuntimeError("PYTORCH/CUDA CHECK FAILED")
print("STAGE 2 PASSED")

# ------------------------------------------------------------
# STAGE 3 - F5-TTS IMPORT TEST
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 3: F5-TTS IMPORT + MODEL INITIALIZATION TEST")
print("=" * 70)

import_test_code = r"""
import f5_tts
print("f5_tts import: OK")
print("f5_tts version:", getattr(f5_tts, "__version__", "unknown"))
print("Loading f5_tts.infer.infer_gradio...")
from f5_tts.infer.infer_gradio import app
print("F5_TTS_INFER_GRADIO_IMPORT_OK")
"""

import_result = subprocess.run([sys.executable, "-c", import_test_code], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print(import_result.stdout[-35000:])
if import_result.returncode != 0:
    print("F5-TTS IMPORT FAILED - NGROK WILL NOT BE STARTED")
    raise RuntimeError("F5-TTS IMPORT TEST FAILED")
print("STAGE 3 PASSED")

# ------------------------------------------------------------
# Create wrapper
# ------------------------------------------------------------
wrapper_code = __WRAPPER_CODE__
with open("master_wrapper_launcher.py", "w", encoding="utf-8") as f:
    f.write(wrapper_code)
print("Wrapper file created successfully")

# ------------------------------------------------------------
# STAGE 4 - START SERVER
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 4: STARTING F5-TTS SERVER")
print("=" * 70)

log_file = open("f5tts_server.log", "w", buffering=1)
server_process = subprocess.Popen([sys.executable, "master_wrapper_launcher.py"], stdout=log_file, stderr=subprocess.STDOUT, text=True)
print("F5-TTS PID:", server_process.pid)

# ------------------------------------------------------------
# Wait until IPv4 127.0.0.1:7860 is really listening.
# ------------------------------------------------------------
print("Waiting for localhost:7860...")
server_ready = False

for attempt in range(180):
    time.sleep(2)

    if server_process.poll() is not None:
        log_file.flush()
        print("\n" + "=" * 70)
        print("F5-TTS SERVER PROCESS DIED")
        print("=" * 70)
        try:
            with open("f5tts_server.log", "r", encoding="utf-8", errors="ignore") as f:
                print(f.read()[-35000:])
        except Exception as log_error:
            print("Could not read server log:", log_error)
        raise RuntimeError("F5-TTS SERVER CRASHED BEFORE PORT 7860 OPENED")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect(("127.0.0.1", 7860))
        sock.close()
        server_ready = True
        print("\n" + "=" * 70)
        print("F5-TTS PORT 7860 IS READY")
        print("=" * 70)
        break
    except Exception:
        sock.close()

    if attempt % 5 == 0:
        print("Still waiting... " + str(attempt * 2) + " seconds")

if not server_ready:
    log_file.flush()
    print("F5-TTS PORT 7860 TIMEOUT")
    try:
        with open("f5tts_server.log", "r", encoding="utf-8", errors="ignore") as f:
            print(f.read()[-35000:])
    except Exception:
        pass
    raise RuntimeError("F5-TTS DID NOT OPEN PORT 7860 WITHIN 360 SECONDS")

# ------------------------------------------------------------
# STAGE 5 - NGROK ONLY AFTER 7860 IS READY
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("STAGE 5: STARTING NGROK")
print("=" * 70)

from pyngrok import ngrok
ngrok.set_auth_token(NGROK_TOKEN)
try:
    ngrok.kill()
except Exception:
    pass

public_url = ngrok.connect(addr="127.0.0.1:7860", proto="http", name="f5_node", hostname=NGROK_DOMAIN)
print("F5-TTS DEPLOYMENT ACTIVE")
print("PUBLIC URL:", public_url)

while True:
    time.sleep(60)
'''

                notebook_source = notebook_source.replace("__NGROK_TOKEN__", repr(ngrok_auth))
                notebook_source = notebook_source.replace("__NGROK_DOMAIN__", repr(ngrok_domain))
                notebook_source = notebook_source.replace("__WRAPPER_CODE__", repr(wrapper_app_script))

                notebook_content = {
                    "cells": [{
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": [line + "\n" for line in notebook_source.splitlines()],
                    }],
                    "metadata": {
                        "kernelspec": {
                            "display_name": "Python 3",
                            "language": "python",
                            "name": "python3",
                        }
                    },
                    "nbformat": 4,
                    "nbformat_minor": 4,
                }

                with open("active_worker.ipynb", "w", encoding="utf-8") as f:
                    json.dump(notebook_content, f, indent=2)

                metadata = {
                    "id": f"{kaggle_username}/f5-tts-custom-node-v2",
                    "title": "F5 TTS Custom Node V2",
                    "code_file": "active_worker.ipynb",
                    "language": "python",
                    "kernel_type": "notebook",
                    "is_private": True,
                    "enable_gpu": True,
                    "enable_internet": True,
                }

                with open("kernel-metadata.json", "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2)

                result = subprocess.run(
                    ["kaggle", "kernels", "push", "-p", "."],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    st.success("🎉 Personal T4 Node deployment start ho gayi!")
                    st.info(
                        "F5-TTS pehle install + CUDA check + import/model initialization complete karega. "
                        "Ngrok sirf tab start hoga jab localhost:7860 actually ready hoga."
                    )
                    st.markdown(f"### 🔗 [Open Your F5-TTS Web UI](https://{ngrok_domain})")
                    st.caption("Agar page immediately open na ho to F5-TTS startup complete hone ka wait karein.")
                else:
                    st.error("Kaggle CLI Error:\n\n" + (result.stderr if result.stderr else result.stdout))

            except Exception as e:
                st.error(f"System Error: {str(e)}")
