import streamlit as st
import json
import os
import subprocess
import urllib.parse

st.set_page_config(page_title="Multi-User F5-TTS Core Hub", page_icon="🎛️", layout="centered")

st.title("🎛️ Multi-User F5-TTS Cloud Hub")
st.write("Apna Kaggle Token aur Ngrok Credentials dalein aur background mein free T4 GPU instant start karein.")

with st.form("user_node_form"):
    st.subheader("1. Kaggle Authentication")
    kaggle_username = st.text_input("Kaggle Username", placeholder="e.g., ahmadkhan")
    kaggle_key = st.text_input("Kaggle API Key", type="password", placeholder="e.g., 8f3c7ea...")

    st.subheader("2. Ngrok Multi-Tunnel Setup")
    ngrok_auth = st.text_input("Ngrok Auth Token", type="password", placeholder="e.g., 2Xf...")
    ngrok_domain = st.text_input("Ngrok Static Domain (Unique per user)", placeholder="e.g., your-unique-id.ngrok-free.app")

    submit_btn = st.form_submit_button("🚀 Deploy My Personal T4 Node")

whatsapp_num = "923097647772"
raw_msg = "Hello M Yousaf! I need guidance regarding the F5-TTS Voice Cloning setup. Kindly assist me."
encoded_msg = urllib.parse.quote(raw_msg)

if submit_btn:
    if not (kaggle_username and kaggle_key and ngrok_auth and ngrok_domain):
        st.error("Meharbani karke saari fields fill karein!")
    else:
        with st.spinner("Kaggle API trigger ho rahi hai... T4 Node provision ho raha hai."):
            try:
                os.environ["KAGGLE_USERNAME"] = kaggle_username
                os.environ["KAGGLE_API_TOKEN"] = kaggle_key

                # Dynamic Custom Wrapper UI Launcher Injection Script
                wrapper_app_script = f"""
import gradio as gr
import os
import time

# F5-TTS ki built-in running application interface layer fetch karna
from f5_tts.infer.infer_gradio import app as f5_original_app

custom_css = ".gradio-container {{background-color: #111111; color: #ffffff; font-family: 'Poppins', sans-serif;}}"
branding_html = '''
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);">
    <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: white;">Welcome to Advanced F5-TTS Portal</h1>
    <p style="margin: 5px 0 15px 0; font-size: 16px; opacity: 0.9; color: #e2e8f0;">Dynamic Multi-User Infrastructure Enabled</p>
    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 10px 0;">
    <p style="margin: 5px 0; font-weight: 500; font-size: 15px; color: #f7fafc;">🛠️ Build, Designed & Optimized by <b>M Yousaf</b></p>
    <a href="https://wa.me{whatsapp_num}?text={encoded_msg}" target="_blank" style="display: inline-flex; align-items: center; background-color: #25D366; color: white; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: 600; font-size: 14px; margin-top: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
        <img src="https://wikimedia.org" style="width: 20px; margin-right: 8px;"/> Get Professional Guide & Support
    </a>
</div>
'''

with gr.Blocks(css=custom_css, title="F5-TTS Voice Portal | M Yousaf") as master_demo:
    # 1. Injecting your custom Premium Header Card
    gr.HTML(branding_html)

    # 2. Injecting custom title information field
    with gr.Row():
        file_title = gr.Textbox(label="💾 Set Output Audio Download Name (Optional)", placeholder="e.g., Cloned_Speech_Yousaf_Project")

    # 3. Embedding the full default layout interface inside your wrapper
    with gr.Row():
        rendered_f5_app = f5_original_app.render()

# Launching Master Wrapper on Port 7860
master_demo.queue().launch(port=7860, host='0.0.0.0')
"""

                notebook_content = {
                    "cells": [
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": [
                                "import os\n",
                                "import subprocess\n",
                                "# Background cleanup process tags\n",
                                "!fuser -k 7860/tcp || true\n",
                                "!pkill -f master_wrapper_launcher.py || true\n",
                                "!pkill -f f5-tts || true\n",
                                f"NGROK_TOKEN = '{ngrok_auth}'\n",
                                f"NGROK_DOMAIN = '{ngrok_domain}'\n",
                                "!pip install pyngrok f5-tts gradio\n",
                                "from pyngrok import ngrok\n",
                                "import time\n",
                                "ngrok.set_auth_token(NGROK_TOKEN)\n",
                                f'with open("master_wrapper_launcher.py", "w") as f: f.write("""{wrapper_app_script.replace(chr(34) * 3, chr(92) + chr(34) * 3)}""")\n',
                                "# Parent application execution bypass trigger\n",
                                'subprocess.run("nohup python master_wrapper_launcher.py > launcher.log 2>&1 &\\n", shell=True, executable="/bin/bash")\n',
                                "time.sleep(5)\n",
                                "import socket\n",
                                "deadline = time.time() + 180\n",
                                "while time.time() < deadline:\n",
                                "    try:\n",
                                "        with socket.create_connection(('127.0.0.1', 7860), timeout=3):\n",
                                "            break\n",
                                "    except OSError:\n",
                                "        time.sleep(3)\n",
                                "else:\n",
                                "    print('===== F5-TTS LAUNCHER LOG =====')\n",
                                "    try:\n",
                                "        with open('launcher.log', 'r', encoding='utf-8', errors='replace') as log_file:\n",
                                "            print(log_file.read())\n",
                                "    except Exception as log_error:\n",
                                "        print('Unable to read launcher.log:', log_error)\n",
                                "    raise RuntimeError('F5-TTS did not start listening on 127.0.0.1:7860')\n",
                                "try:\n",
                                "    for tunnel in ngrok.get_tunnels():\n",
                                "        ngrok.disconnect(tunnel.public_url)\n",
                                "except Exception:\n",
                                "    pass\n",
                                "public_url = ngrok.connect('127.0.0.1:7860', name='f5_node', hostname=NGROK_DOMAIN)\n",
                                "print('Wrapper Deployment Active:', public_url)\n",
                                "while True: time.sleep(60)"
                            ]
                        }
                    ],
                    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
                    "nbformat": 4,
                    "nbformat_minor": 4
                }

                with open("active_worker.ipynb", "w") as f:
                    json.dump(notebook_content, f)

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

                result = subprocess.run(["kaggle", "kernels", "push", "-p", "."], capture_output=True, text=True)

                if "successfully" in result.stdout.lower() or result.returncode == 0:
                    st.success(f"🎉 Aapka personal T4 Node background mein start ho chuka hai!")
                    st.markdown(f"### 🔗 [Click Here To Open Your F5-TTS Web UI](https://{ngrok_domain})")
                else:
                    st.error(f"Kaggle CLI Error: {result.stderr if result.stderr else result.stdout}")

            except Exception as e:
                st.error(f"System Error: {str(e)}")
