import streamlit as st
import json
import os
import subprocess

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

if submit_btn:
    if not (kaggle_username and kaggle_key and ngrok_auth and ngrok_domain):
        st.error("Meharbani karke saari fields fill karein!")
    else:
        with st.spinner("Kaggle API trigger ho rahi hai... T4 Node provision ho raha hai."):
            try:
                # Kaggle credentials configure karna environment runtime ke liye
                os.environ["KAGGLE_USERNAME"] = kaggle_username
                os.environ["KAGGLE_KEY"] = kaggle_key
                
                # Dynamic Notebook setup
                notebook_content = {
                    "cells": [
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": [
                                f"NGROK_TOKEN = '{ngrok_auth}'\n",
                                f"NGROK_DOMAIN = '{ngrok_domain}'\n",
                                "!pip install pyngrok f5-tts gradio\n",
                                "from pyngrok import ngrok\n",
                                "import subprocess\n",
                                "import time\n",
                                "ngrok.set_auth_token(NGROK_TOKEN)\n",
                                "# Background execution start karna local model serve port par\n",
                                "subprocess.Popen(['f5-tts_infer-gradio', '--port', '7860', '--host', '0.0.0.0'])\n",
                                "time.sleep(15)\n",
                                "# Edge custom static proxy trigger mapping\n",
                                "public_url = ngrok.connect(7860, name='f5_node', hostname=NGROK_DOMAIN)\n",
                                "print('Node Active:', public_url)\n",
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
                    "id": f"{kaggle_username}/f5-tts-worker-node",
                    "title": "F5 TTS Worker Node",
                    "code_file": "active_worker.ipynb",
                    "language": "python",
                    "kernel_type": "notebook",
                    "is_private": True,
                    "enable_gpu": True,
                    "enable_internet": True
                }
                with open("kernel-metadata.json", "w") as f:
                    json.dump(metadata, f)
                
                # Kaggle Python SDK process pipeline
                result = subprocess.run(["kaggle", "kernels", "push", "-p", "."], capture_output=True, text=True)
                
                if "successfully" in result.stdout.lower() or result.returncode == 0:
                    st.success(f"🎉 Aapka personal T4 Node background mein start ho chuka hai!")
                    st.markdown(f"### 🔗 [Click Here To Open Your F5-TTS Web UI](https://{ngrok_domain})")
                else:
                    st.error(f"Kaggle CLI Error: {result.stderr if result.stderr else result.stdout}")
                    
            except Exception as e:
                st.error(f"System Error: {str(e)}")
