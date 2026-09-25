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

# WhatsApp auto draft message setting
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
                
                # Dynamic Custom Gradio App Launcher Injection string
                gradio_override_script = f"""
import gradio as gr
import shutil
import os
import time

def process_voice_clone(text_input, reference_audio, file_title):
    # Base F5-TTS model inference call runs here
    # (Yeh placeholder actual core function call back represent karta hai)
    generated_temp_file = "temp_output.wav" 
    
    # Custom Name Override Logic
    clean_title = "".join([c for c in file_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    if not clean_title:
        clean_title = "cloned_voice"
        
    final_output_path = f"{{clean_title}}.wav"
    shutil.copy(generated_temp_file, final_output_path)
    return final_output_path

# Custom Premium Styling & Contact Badge HTML
custom_css = ".gradio-container {{background-color: #f7f9fc; font-family: 'Poppins', sans-serif;}}"
branding_html = '''
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
    <h1 style="margin: 0; font-size: 28px; font-weight: 700;">Welcome to Advanced F5-TTS</h1>
    <p style="margin: 5px 0 15px 0; font-size: 16px; opacity: 0.9;">Professional Voice Cloning Portal</p>
    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.2); margin: 10px 0;">
    <p style="margin: 5px 0; font-weight: 500; font-size: 14px;">🛠️ Build & Optimized by <b>M Yousaf</b></p>
    <a href="https://wa.me{whatsapp_num}?text={encoded_msg}" target="_blank" style="display: inline-flex; align-items: center; background-color: #25D366; color: white; padding: 8px 16px; border-radius: 30px; text-decoration: none; font-weight: 600; font-size: 14px; margin-top: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
        <img src="https://wikimedia.org" style="width: 20px; margin-right: 8px;"/> Get Expert Guidance
    </a>
</div>
'''

with gr.Blocks(css=custom_css, title="F5-TTS Voice Portal") as demo:
    gr.HTML(branding_html)
    with gr.Row():
        with gr.Column():
            title_input = gr.Textbox(label="Save Audio As (Custom File Name)", placeholder="e.g., My_Project_Voice")
            text_field = gr.Textbox(label="Text to Speech (Input text)", lines=3)
            audio_ref = gr.Audio(label="Reference Voice Audio File Source", type="filepath")
            generate_btn = gr.Button("🚀 Generate Clone Voice", variant="primary")
        with gr.Column():
            audio_output = gr.Audio(label="Download Cloned Output Track File")
            
    generate_btn.click(
        fn=process_voice_clone,
        inputs=[text_field, audio_ref, title_input],
        outputs=audio_output
    )

demo.queue().launch(port=7860, host='0.0.0.0')
"""
                
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
                                f"with open('custom_gradio_app.py', 'w') as f: f.write('''{gradio_override_script}''')\n",
                                "subprocess.Popen(['python', 'custom_gradio_app.py'])\n",
                                "time.sleep(15)\n",
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
                
                result = subprocess.run(["kaggle", "kernels", "push", "-p", "."], capture_output=True, text=True)
                
                if "successfully" in result.stdout.lower() or result.returncode == 0:
                    st.success(f"🎉 Aapka personal T4 Node background mein start ho chuka hai!")
                    st.markdown(f"### 🔗 [Click Here To Open Your F5-TTS Web UI](https://{ngrok_domain})")
                else:
                    st.error(f"Kaggle CLI Error: {result.stderr if result.stderr else result.stdout}")
                    
            except Exception as e:
                st.error(f"System Error: {str(e)}")
