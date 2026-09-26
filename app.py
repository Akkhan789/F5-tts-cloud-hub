import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
import urllib.error

import streamlit as st

st.set_page_config(
    page_title="Multi-User F5-TTS Core Hub",
    page_icon="🎛️",
    layout="centered",
)

st.title("🎛️ Multi-User F5-TTS Cloud Hub")
st.write(
    "Kaggle T4 par F5-TTS deploy karein. Ngrok tunnel sirf tab start hoga "
    "jab F5-TTS ka HTTP service actually ready ho."
)

with st.form("user_node_form"):
    st.subheader("1. Kaggle Authentication")
    kaggle_username = st.text_input(
        "Kaggle Username",
        placeholder="e.g. your_kaggle_username",
    )
    kaggle_key = st.text_input(
        "Kaggle API Key",
        type="password",
        placeholder="Kaggle API token",
    )

    st.subheader("2. Ngrok Setup")
    ngrok_auth = st.text_input(
        "Ngrok Auth Token",
        type="password",
        placeholder="Ngrok auth token",
    )
    ngrok_domain = st.text_input(
        "Ngrok Static Domain",
        placeholder="e.g. your-name.ngrok-free.app",
    )

    submit_btn = st.form_submit_button("🚀 Deploy My Personal T4 Node")

whatsapp_num = "923097647772"
raw_msg = (
    "Hello M Yousaf! I need guidance regarding the F5-TTS Voice Cloning "
    "setup. Kindly assist me."
)
encoded_msg = urllib.parse.quote(raw_msg)


def kaggle_status(kernel_id: str):
    """Return Kaggle CLI status output and a normalized state."""
    try:
        result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_id],
            capture_output=True,
            text=True,
            timeout=30,
        )
        raw = (result.stdout or result.stderr or "").strip()
        upper = raw.upper()
        if "ERROR" in upper or "FAILED" in upper:
            state = "FAILED"
        elif "RUNNING" in upper or "QUEUED" in upper or "WAITING" in upper:
            state = "RUNNING"
        elif "COMPLETE" in upper or "SUCCESS" in upper:
            state = "COMPLETE"
        else:
            state = "UNKNOWN"
        return state, raw
    except Exception as exc:
        return "UNKNOWN", repr(exc)


def public_service_state(domain: str):
    """Probe the actual public URL; ERR_NGROK_8012 is not considered ready."""
    url = "https://" + domain.strip().rstrip("/") + "/"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "F5-TTS-Deployment-Health-Check"},
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            status = response.status
            body = response.read(5000).decode("utf-8", errors="ignore")
        if 200 <= status < 500 and "ERR_NGROK_8012" not in body:
            return True, f"HTTP {status}"
        return False, f"HTTP {status} / upstream not ready"
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(5000).decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        if "ERR_NGROK_8012" in body:
            return False, "ngrok agent reachable, upstream localhost:7860 refused"
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, str(exc)


if submit_btn:
    if not all(
        [
            kaggle_username.strip(),
            kaggle_key.strip(),
            ngrok_auth.strip(),
            ngrok_domain.strip(),
        ]
    ):
        st.error("Meharbani karke saari fields fill karein!")
    else:
        with st.spinner(
            "Kaggle node deploy ho raha hai. F5-TTS install aur startup "
            "complete hone ke baad hi service expose hogi..."
        ):
            try:
                os.environ["KAGGLE_USERNAME"] = kaggle_username.strip()
                os.environ["KAGGLE_API_TOKEN"] = kaggle_key.strip()

                # =========================================================
                # F5-TTS WRAPPER
                # =========================================================
                # IMPORTANT:
                # No separate F5-TTS import test is performed here.
                # The wrapper itself performs the one real import/startup.
                # This removes the old double-import/model-load problem.
                # =========================================================
                wrapper_app_script = r'''
import traceback

print("=" * 80)
print("F5-TTS NODE START")
print("=" * 80)

try:
    import gradio as gr

    print("GRADIO_VERSION =", getattr(gr, "__version__", "unknown"))
    print("Loading official F5-TTS application...")

    # Official F5-TTS documents this component usage.
    from f5_tts.infer.infer_gradio import app as f5_original_app

    print("F5_TTS_IMPORT_OK")
    print("F5_TTS_APP_OBJECT_OK")

except Exception as exc:
    print("=" * 80)
    print("F5-TTS STARTUP FAILED")
    print("ERROR:", repr(exc))
    traceback.print_exc()
    print("=" * 80)
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
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 25px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,.30);
">
    <h1 style="margin:0;font-size:28px;font-weight:700;color:white;">
        Welcome to Advanced F5-TTS Portal
    </h1>
    <p style="margin:5px 0 15px;font-size:16px;color:#e2e8f0;">
        Dynamic Multi-User Infrastructure Enabled
    </p>
    <hr style="border:0;border-top:1px solid rgba(255,255,255,.20);margin:10px 0;">
    <p style="margin:5px 0;font-weight:500;font-size:15px;color:#f7fafc;">
        🛠️ Build, Designed &amp; Optimized by <b>M Yousaf</b>
    </p>
    <a
        href="https://wa.me/923097647772?text=Hello%20M%20Yousaf%21%20I%20need%20guidance%20regarding%20the%20F5-TTS%20Voice%20Cloning%20setup.%20Kindly%20assist%20me."
        target="_blank"
        style="display:inline-flex;align-items:center;background:#25D366;color:white;padding:10px 20px;border-radius:30px;text-decoration:none;font-weight:600;font-size:14px;margin-top:12px;"
    >
        Get Professional Guide &amp; Support
    </a>
</div>
"""

print("Building custom Gradio wrapper...")

with gr.Blocks(
    css=custom_css,
    title="F5-TTS Voice Portal | M Yousaf",
) as master_demo:
    gr.HTML(branding_html)

    with gr.Row():
        gr.Textbox(
            label="💾 Set Output Audio Download Name (Optional)",
            placeholder="e.g. Cloned_Speech_Yousaf_Project",
        )

    with gr.Row():
        f5_original_app.render()

print("F5-TTS UI BUILD OK")
print("Launching HTTP service on 0.0.0.0:7860")

master_demo.queue().launch(
    server_name="0.0.0.0",
    server_port=7860,
    show_error=True,
)
'''

                # =========================================================
                # KAGGLE NOTEBOOK
                # =========================================================
                notebook_source = r'''
import os
import sys
import time
import socket
import subprocess
import urllib.request

NGROK_TOKEN = __NGROK_TOKEN__
NGROK_DOMAIN = __NGROK_DOMAIN__
WRAPPER_CODE = __WRAPPER_CODE__

print("=" * 80)
print("KAGGLE F5-TTS NODE BOOT")
print("=" * 80)

# ============================================================
# 1. CLEAN ONLY PORT 7860
# ============================================================
print("Cleaning port 7860...")
subprocess.run(
    "fuser -k 7860/tcp || true",
    shell=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# ============================================================
# 2. INSTALL
# ============================================================
# Pin the currently published F5-TTS release so a future package
# update cannot silently change the environment.
F5_VERSION = "1.1.22"

print("=" * 80)
print("INSTALLING F5-TTS", F5_VERSION)
print("=" * 80)

install = subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--no-cache-dir",
        f"f5-tts=={F5_VERSION}",
        "gradio>=6.15.0",
        "pyngrok",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

print(install.stdout[-30000:])

if install.returncode != 0:
    raise RuntimeError("F5-TTS PIP INSTALL FAILED")

print("F5-TTS INSTALL OK")

# ============================================================
# 3. GPU CHECK
# ============================================================
print("=" * 80)
print("PYTORCH / GPU CHECK")
print("=" * 80)

gpu_check = subprocess.run(
    [
        sys.executable,
        "-c",
        (
            "import torch; "
            "print('TORCH=', torch.__version__); "
            "print('CUDA_AVAILABLE=', torch.cuda.is_available()); "
            "print('CUDA_VERSION=', torch.version.cuda); "
            "print('GPU=', torch.cuda.get_device_name(0) "
            "if torch.cuda.is_available() else 'NONE')"
        ),
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

print(gpu_check.stdout)

if gpu_check.returncode != 0:
    raise RuntimeError("PYTORCH/GPU CHECK FAILED")

# ============================================================
# 4. WRITE WRAPPER
# ============================================================
with open(
    "master_wrapper_launcher.py",
    "w",
    encoding="utf-8",
) as f:
    f.write(WRAPPER_CODE)

print("Wrapper file created")

# ============================================================
# 5. START F5-TTS
# ============================================================
print("=" * 80)
print("STARTING F5-TTS")
print("=" * 80)

log_file = open(
    "f5tts_server.log",
    "w",
    buffering=1,
)

server = subprocess.Popen(
    [sys.executable, "master_wrapper_launcher.py"],
    stdout=log_file,
    stderr=subprocess.STDOUT,
    text=True,
)

print("F5-TTS PID =", server.pid)

# ============================================================
# 6. WAIT FOR REAL HTTP SERVICE
# ============================================================
# TCP port alone is not enough. We require an actual HTTP response
# before starting ngrok. This directly prevents ERR_NGROK_8012.
print("=" * 80)
print("WAITING FOR F5-TTS HTTP SERVICE")
print("=" * 80)

ready = False

for second in range(1, 601):
    time.sleep(1)

    if server.poll() is not None:
        log_file.flush()
        print("=" * 80)
        print("F5-TTS PROCESS EXITED")
        print("=" * 80)

        try:
            with open(
                "f5tts_server.log",
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as f:
                print(f.read()[-50000:])
        except Exception as exc:
            print("Could not read F5-TTS log:", repr(exc))

        raise RuntimeError(
            "F5-TTS STOPPED BEFORE BECOMING READY"
        )

    # First check that something is listening.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    tcp_ok = False

    try:
        sock.connect(("127.0.0.1", 7860))
        tcp_ok = True
    except Exception:
        pass
    finally:
        sock.close()

    if not tcp_ok:
        if second % 15 == 0:
            print("F5-TTS still starting:", second, "seconds")
        continue

    # Then require an HTTP response.
    try:
        request = urllib.request.Request(
            "http://127.0.0.1:7860/",
            headers={"User-Agent": "F5-TTS-health-check"},
        )

        with urllib.request.urlopen(request, timeout=5) as response:
            status = response.status

        if 200 <= status < 500:
            ready = True
            print("=" * 80)
            print("F5-TTS HTTP SERVICE READY - STATUS", status)
            print("=" * 80)
            break

    except Exception:
        pass

    if second % 15 == 0:
        print(
            "Port is open but HTTP service is not ready yet:",
            second,
            "seconds",
        )

if not ready:
    log_file.flush()
    print("=" * 80)
    print("F5-TTS HTTP STARTUP TIMEOUT")
    print("=" * 80)

    try:
        with open(
            "f5tts_server.log",
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:
            print(f.read()[-50000:])
    except Exception:
        pass

    raise RuntimeError(
        "F5-TTS DID NOT BECOME HTTP-READY WITHIN 600 SECONDS"
    )

# ============================================================
# 7. ONLY AFTER HTTP READY: NGROK
# ============================================================
print("=" * 80)
print("STARTING NGROK")
print("=" * 80)

from pyngrok import ngrok

ngrok.set_auth_token(NGROK_TOKEN)

try:
    ngrok.kill()
except Exception:
    pass

public_url = ngrok.connect(
    addr="127.0.0.1:7860",
    proto="http",
    name="f5_node",
    hostname=NGROK_DOMAIN,
)

print("=" * 80)
print("F5-TTS IS LIVE")
print("PUBLIC URL =", public_url)
print("=" * 80)

while True:
    time.sleep(60)
'''

                notebook_source = (
                    notebook_source
                    .replace("__NGROK_TOKEN__", repr(ngrok_auth.strip()))
                    .replace("__NGROK_DOMAIN__", repr(ngrok_domain.strip()))
                    .replace("__WRAPPER_CODE__", repr(wrapper_app_script))
                )

                notebook_content = {
                    "cells": [
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": [
                                line + "\n"
                                for line in notebook_source.splitlines()
                            ],
                        }
                    ],
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

                with open(
                    "active_worker.ipynb",
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(notebook_content, f, indent=2)

                metadata = {
                    "id": (
                        f"{kaggle_username.strip()}/"
                        "f5-tts-custom-node-v2"
                    ),
                    "title": "F5 TTS Custom Node V2",
                    "code_file": "active_worker.ipynb",
                    "language": "python",
                    "kernel_type": "notebook",
                    "is_private": True,
                    "enable_gpu": True,
                    "enable_internet": True,
                }

                with open(
                    "kernel-metadata.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(metadata, f, indent=2)

                result = subprocess.run(
                    ["kaggle", "kernels", "push", "-p", "."],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    st.error(
                        "Kaggle deployment failed:\n\n"
                        + (
                            result.stderr
                            if result.stderr
                            else result.stdout
                        )
                    )
                else:
                    kernel_id = (
                        kaggle_username.strip()
                        + "/f5-tts-custom-node-v2"
                    )
                    domain = ngrok_domain.strip()

                    st.session_state["deployment"] = {
                        "kernel_id": kernel_id,
                        "domain": domain,
                    }

                    st.success("✅ Kaggle T4 deployment submitted.")
                    st.info(
                        "🔎 V3 ab deployment ko verify karega. Sirf 'queued/running' "
                        "ko LIVE nahi maana jayega. Web UI tabhi show hoga jab public "
                        "ngrok URL actual F5-TTS response dega."
                    )

            except Exception as exc:
                st.error("System Error: " + repr(exc))

# ============================================================
# LIVE DEPLOYMENT MONITOR
# ============================================================
if "deployment" in st.session_state:
    dep = st.session_state["deployment"]
    kernel_id = dep["kernel_id"]
    domain = dep["domain"]

    st.divider()
    st.subheader("🔎 Live Deployment Monitor")
    st.code("Kaggle kernel: " + kernel_id)

    if st.button("🔄 Check F5-TTS Status", use_container_width=True):
        with st.spinner("Kaggle status aur ngrok service check ho rahi hai..."):
            state, raw_status = kaggle_status(kernel_id)
            ready, public_detail = public_service_state(domain)

        if state == "FAILED":
            st.error("❌ Kaggle kernel FAILED")
        elif ready:
            st.success("🟢 F5-TTS Web UI is actually reachable.")
            st.markdown(
                f"### 🔗 [Open F5-TTS Web UI](https://{domain})"
            )
            st.caption("Public URL ne actual HTTP response diya hai; ERR_NGROK_8012 detect nahi hua.")
        elif state == "RUNNING":
            st.warning("🟡 Kaggle kernel RUNNING hai, lekin F5-TTS Web UI abhi ready nahi hai.")
            st.write("Public check:", public_detail)
            st.caption("Model download/initialization complete hone ka wait karein, phir 'Check F5-TTS Status' dobara press karein.")
        elif state == "COMPLETE":
            st.error("🔴 Kaggle run COMPLETE ho gaya lekin Web UI reachable nahi hai. Iska matlab F5-TTS startup likely fail/exit hua.")
            st.write("Public check:", public_detail)
        else:
            st.warning("🟠 Kaggle status abhi clearly determine nahi hua.")
            st.write("Public check:", public_detail)

        with st.expander("Kaggle status raw output"):
            st.code(raw_status or "No status output returned.")
