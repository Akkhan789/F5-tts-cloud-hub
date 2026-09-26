import streamlit as st
import json
import os
import subprocess
import urllib.parse

st.set_page_config(
    page_title="Multi-User F5-TTS Core Hub",
    page_icon="🎛️",
    layout="centered"
)

st.title("🎛️ Multi-User F5-TTS Cloud Hub")
st.write(
    "Apna Kaggle Token aur Ngrok Credentials dalein "
    "aur background mein free T4 GPU instant start karein."
)

with st.form("user_node_form"):

    st.subheader("1. Kaggle Authentication")

    kaggle_username = st.text_input(
        "Kaggle Username",
        placeholder="e.g., ahmadkhan"
    )

    kaggle_key = st.text_input(
        "Kaggle API Key",
        type="password",
        placeholder="e.g., 8f3c7ea..."
    )

    st.subheader("2. Ngrok Multi-Tunnel Setup")

    ngrok_auth = st.text_input(
        "Ngrok Auth Token",
        type="password",
        placeholder="e.g., 2Xf..."
    )

    ngrok_domain = st.text_input(
        "Ngrok Static Domain (Unique per user)",
        placeholder="e.g., your-unique-id.ngrok-free.app"
    )

    submit_btn = st.form_submit_button(
        "🚀 Deploy My Personal T4 Node"
    )


whatsapp_num = "923097647772"

raw_msg = (
    "Hello M Yousaf! I need guidance regarding "
    "the F5-TTS Voice Cloning setup. Kindly assist me."
)

encoded_msg = urllib.parse.quote(raw_msg)


if submit_btn:

    if not (
        kaggle_username
        and kaggle_key
        and ngrok_auth
        and ngrok_domain
    ):
        st.error("Meharbani karke saari fields fill karein!")

    else:

        with st.spinner(
            "Kaggle API trigger ho rahi hai... "
            "T4 Node provision ho raha hai."
        ):

            try:

                os.environ["KAGGLE_USERNAME"] = kaggle_username
                os.environ["KAGGLE_API_TOKEN"] = kaggle_key

                # =====================================================
                # CUSTOM F5-TTS WRAPPER
                # =====================================================

                wrapper_app_script = f'''
import gradio as gr
import time

# F5-TTS ki built-in Gradio application import
from f5_tts.infer.infer_gradio import app as f5_original_app


# ============================================================
# CUSTOM CSS
# ============================================================

custom_css = """
.gradio-container {{
    background-color: #111111 !important;
    color: #ffffff !important;
    font-family: 'Poppins', sans-serif !important;
}}

body {{
    background-color: #111111 !important;
}}
"""


# ============================================================
# PREMIUM HEADER
# ============================================================

branding_html = """
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 25px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.1);
">

    <h1 style="
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: white;
    ">
        Welcome to Advanced F5-TTS Portal
    </h1>

    <p style="
        margin: 5px 0 15px 0;
        font-size: 16px;
        opacity: 0.9;
        color: #e2e8f0;
    ">
        Dynamic Multi-User Infrastructure Enabled
    </p>

    <hr style="
        border: 0;
        border-top: 1px solid rgba(255,255,255,0.2);
        margin: 10px 0;
    ">

    <p style="
        margin: 5px 0;
        font-weight: 500;
        font-size: 15px;
        color: #f7fafc;
    ">
        🛠️ Build, Designed & Optimized by
        <b>M Yousaf</b>
    </p>

    <a
        href="https://wa.me/{whatsapp_num}?text={encoded_msg}"
        target="_blank"
        style="
            display: inline-flex;
            align-items: center;
            background-color: #25D366;
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            margin-top: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        "
    >
        Get Professional Guide & Support
    </a>

</div>
"""


# ============================================================
# MASTER WRAPPER
# ============================================================

with gr.Blocks(
    css=custom_css,
    title="F5-TTS Voice Portal | M Yousaf"
) as master_demo:

    # Premium Header
    gr.HTML(branding_html)

    # Output filename field
    with gr.Row():

        file_title = gr.Textbox(
            label="💾 Set Output Audio Download Name (Optional)",
            placeholder="e.g., Cloned_Speech_Yousaf_Project"
        )

    # Original F5-TTS interface
    with gr.Row():

        f5_original_app.render()


print("==============================================")
print("F5-TTS WRAPPER STARTING")
print("==============================================")

master_demo.queue().launch(
    server_name="0.0.0.0",
    server_port=7860,
    show_error=True
)
'''

                # =====================================================
                # KAGGLE NOTEBOOK
                # =====================================================

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
                                "import time\n",
                                "import socket\n",
                                "import subprocess\n",
                                "\n",

                                "# =====================================================\n",
                                "# CLEAN OLD PROCESSES\n",
                                "# =====================================================\n",
                                "\n",

                                "!fuser -k 7860/tcp || true\n",
                                "!pkill -f master_wrapper_launcher.py || true\n",
                                "!pkill -f f5-tts || true\n",
                                "\n",

                                f"NGROK_TOKEN = {ngrok_auth!r}\n",
                                f"NGROK_DOMAIN = {ngrok_domain!r}\n",
                                "\n",

                                "# =====================================================\n",
                                "# INSTALL F5-TTS\n",
                                "# =====================================================\n",
                                "\n",

                                "print('Installing F5-TTS...')\n",

                                "subprocess.run([\n",
                                "    sys.executable,\n",
                                "    '-m',\n",
                                "    'pip',\n",
                                "    'install',\n",
                                "    '-U',\n",
                                "    'pyngrok',\n",
                                "    'f5-tts'\n",
                                "], check=True)\n",
                                "\n",

                                "print('F5-TTS installation complete.')\n",
                                "\n",

                                "# =====================================================\n",
                                "# VERIFY F5-TTS IMPORT\n",
                                "# =====================================================\n",
                                "\n",

                                "print('Checking F5-TTS installation...')\n",

                                "subprocess.run([\n",
                                "    sys.executable,\n",
                                "    '-c',\n",
                                "    'import f5_tts; print(\\\"F5-TTS IMPORT OK\\\")'\n",
                                "], check=True)\n",
                                "\n",

                                "# =====================================================\n",
                                "# CREATE WRAPPER FILE\n",
                                "# =====================================================\n",
                                "\n",

                                f"wrapper_code = {wrapper_app_script!r}\n",

                                "with open('master_wrapper_launcher.py', 'w', encoding='utf-8') as f:\n",
                                "    f.write(wrapper_code)\n",
                                "\n",

                                "print('Wrapper created successfully.')\n",
                                "\n",

                                "# =====================================================\n",
                                "# START WRAPPER\n",
                                "# =====================================================\n",
                                "\n",

                                "log_file = open('f5tts_server.log', 'w', buffering=1)\n",
                                "\n",

                                "server_process = subprocess.Popen(\n",
                                "    [sys.executable, 'master_wrapper_launcher.py'],\n",
                                "    stdout=log_file,\n",
                                "    stderr=subprocess.STDOUT,\n",
                                "    text=True\n",
                                ")\n",
                                "\n",

                                "print('F5-TTS wrapper PID:', server_process.pid)\n",
                                "\n",

                                "# =====================================================\n",
                                "# WAIT FOR PORT 7860\n",
                                "# =====================================================\n",
                                "\n",

                                "print('Waiting for F5-TTS interface to become ready...')\n",
                                "\n",

                                "server_ready = False\n",
                                "\n",

                                "for attempt in range(180):\n",

                                "    time.sleep(2)\n",
                                "\n",

                                "    # Check if process crashed\n",
                                "    if server_process.poll() is not None:\n",

                                "        log_file.flush()\n",
                                "\n",

                                "        print('\\n==============================================')\n",
                                "        print('F5-TTS PROCESS CRASHED')\n",
                                "        print('==============================================\\n')\n",
                                "\n",

                                "        try:\n",
                                "            with open('f5tts_server.log', 'r', encoding='utf-8', errors='ignore') as f:\n",
                                "                print(f.read()[-15000:])\n",
                                "        except Exception as log_error:\n",
                                "            print('Could not read log:', log_error)\n",
                                "\n",

                                "        raise RuntimeError(\n",
                                "            'F5-TTS wrapper stopped before port 7860 became ready.'\n",
                                "        )\n",
                                "\n",

                                "    # Check IPv4 localhost port\n",
                                "    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n",
                                "    sock.settimeout(1)\n",
                                "\n",

                                "    try:\n",
                                "        sock.connect(('127.0.0.1', 7860))\n",
                                "        server_ready = True\n",
                                "        sock.close()\n",
                                "\n",
                                "        print('\\n==============================================')\n",
                                "        print('F5-TTS PORT 7860 IS READY')\n",
                                "        print('==============================================\\n')\n",
                                "\n",
                                "        break\n",
                                "\n",
                                "    except Exception:\n",
                                "        sock.close()\n",
                                "\n",

                                "    if attempt % 5 == 0:\n",
                                "        print(\n",
                                "            'Still waiting for F5-TTS... '\n",
                                "            + str(attempt * 2)\n",
                                "            + ' seconds'\n",
                                "        )\n",
                                "\n",

                                "# =====================================================\n",
                                "# FAIL IF SERVER NEVER STARTED\n",
                                "# =====================================================\n",
                                "\n",

                                "if not server_ready:\n",

                                "    log_file.flush()\n",
                                "\n",

                                "    print('\\n==============================================')\n",
                                "    print('F5-TTS STARTUP TIMEOUT')\n",
                                "    print('==============================================\\n')\n",
                                "\n",

                                "    try:\n",
                                "        with open('f5tts_server.log', 'r', encoding='utf-8', errors='ignore') as f:\n",
                                "            print(f.read()[-15000:])\n",
                                "    except Exception:\n",
                                "        pass\n",
                                "\n",

                                "    raise RuntimeError(\n",
                                "        'F5-TTS did not open port 7860 within 360 seconds.'\n",
                                "    )\n",
                                "\n",

                                "# =====================================================\n",
                                "# ONLY NOW START NGROK\n",
                                "# =====================================================\n",
                                "\n",

                                "from pyngrok import ngrok\n",
                                "\n",

                                "ngrok.set_auth_token(NGROK_TOKEN)\n",
                                "\n",

                                "print('Starting ngrok tunnel...')\n",
                                "\n",

                                "try:\n",
                                "    ngrok.kill()\n",
                                "except Exception:\n",
                                "    pass\n",
                                "\n",

                                "public_url = ngrok.connect(\n",
                                "    addr='127.0.0.1:7860',\n",
                                "    proto='http',\n",
                                "    name='f5_node',\n",
                                "    hostname=NGROK_DOMAIN\n",
                                ")\n",
                                "\n",

                                "print('\\n==============================================')\n",
                                "print('F5-TTS DEPLOYMENT ACTIVE')\n",
                                "print('PUBLIC URL:', public_url)\n",
                                "print('==============================================\\n')\n",
                                "\n",

                                "# =====================================================\n",
                                "# KEEP KAGGLE SESSION ALIVE\n",
                                "# =====================================================\n",
                                "\n",

                                "while True:\n",
                                "    time.sleep(60)\n"
                            ]
                        }

                    ],

                    "metadata": {
                        "kernelspec": {
                            "display_name": "Python 3",
                            "language": "python",
                            "name": "python3"
                        }
                    },

                    "nbformat": 4,
                    "nbformat_minor": 4
                }

                # =====================================================
                # WRITE NOTEBOOK
                # =====================================================

                with open("active_worker.ipynb", "w") as f:
                    json.dump(notebook_content, f)

                # =====================================================
                # KAGGLE METADATA
                # =====================================================

                metadata = {

                    "id": f"{kaggle_username}/f5-tts-custom-node-v2",

                    "title": "F5 TTS Custom Node V2",

                    "code_file": "active_worker.ipynb",

                    "language": "python",

                    "kernel_type": "notebook",

                    "is_private": True,

                    "enable_gpu": True,

                    "enable_internet": True
                }

                with open("kernel-metadata.json", "w") as f:
                    json.dump(metadata, f)

                # =====================================================
                # PUSH KAGGLE KERNEL
                # =====================================================

                result = subprocess.run(
                    ["kaggle", "kernels", "push", "-p", "."],
                    capture_output=True,
                    text=True
                )

                if (
                    "successfully" in result.stdout.lower()
                    or result.returncode == 0
                ):

                    st.success(
                        "🎉 Aapka personal T4 Node background mein "
                        "start ho chuka hai!"
                    )

                    st.info(
                        "⏳ Pehli dafa F5-TTS dependencies/model load "
                        "hone mein kuch waqt lag sakta hai. "
                        "Link tab open karein jab Kaggle notebook "
                        "7860 ready kar chuki ho."
                    )

                    st.markdown(
                        f"### 🔗 [Click Here To Open Your F5-TTS Web UI]"
                        f"(https://{ngrok_domain})"
                    )

                else:

                    st.error(
                        "Kaggle CLI Error: "
                        + (
                            result.stderr
                            if result.stderr
                            else result.stdout
                        )
                    )

            except Exception as e:

                st.error(
                    f"System Error: {str(e)}"
                )
