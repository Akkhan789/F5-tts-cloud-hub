import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="F5-TTS Personal Server", page_icon="🎙️", layout="centered")

st.title("🎙️ F5-TTS Personal Server")
st.caption("Apna Kaggle + ngrok details dein. Server aapke apne Kaggle GPU par chalega.")


def normalize_domain(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    parsed = urlparse(value)
    return parsed.netloc.lower().strip().rstrip("/")


def verify_kaggle(username: str, token: str):
    env = os.environ.copy()
    env["KAGGLE_USERNAME"] = username.strip()
    env["KAGGLE_API_TOKEN"] = token.strip()
    try:
        result = subprocess.run(
            ["kaggle", "kernels", "list", "--mine", "--page-size", "1"],
            env=env,
            capture_output=True,
            text=True,
            timeout=25,
        )
        return result.returncode == 0, (result.stderr or result.stdout or "").strip()
    except Exception as exc:
        return False, str(exc)


def build_kernel_folder(username: str, kaggle_token: str, ngrok_token: str, domain: str):
    template_path = Path(__file__).with_name("kaggle_node_template.py")
    if not template_path.exists():
        raise FileNotFoundError("kaggle_node_template.py is missing from the GitHub project.")

    template = template_path.read_text(encoding="utf-8")
    node_code = template.replace("__NGROK_TOKEN__", repr(ngrok_token.strip()))
    node_code = node_code.replace("__NGROK_DOMAIN__", repr(domain.strip()))

    suffix = f"{int(time.time())}-{os.urandom(3).hex()}"
    slug = f"f5-tts-server-{suffix}"
    title = f"F5-TTS Server {suffix}"

    folder = Path(tempfile.mkdtemp(prefix="f5tts-kernel-"))
    (folder / "main.py").write_text(node_code, encoding="utf-8")
    metadata = {
        "id": f"{username.strip()}/{slug}",
        "title": title,
        "code_file": "main.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
        "machine_shape": "NvidiaTeslaT4",
    }
    (folder / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return folder, metadata["id"]


def push_kernel(folder: Path, username: str, token: str):
    env = os.environ.copy()
    env["KAGGLE_USERNAME"] = username.strip()
    env["KAGGLE_API_TOKEN"] = token.strip()
    return subprocess.run(
        ["kaggle", "kernels", "push", "-p", str(folder)],
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def wait_for_public_url(domain: str, timeout: int = 900):
    url = "https://" + domain.rstrip("/") + "/"
    started = time.time()
    while time.time() - started < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "F5-TTS-Ready-Check"})
            with urllib.request.urlopen(req, timeout=8) as response:
                body = response.read(10000).decode("utf-8", errors="ignore")
                if 200 <= response.status < 500 and "ERR_NGROK_8012" not in body:
                    return True
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read(10000).decode("utf-8", errors="ignore")
            except Exception:
                body = ""
            if exc.code != 502 and "ERR_NGROK_8012" not in body:
                # The endpoint exists; Gradio may still be warming up.
                if 200 <= exc.code < 500:
                    return True
        except Exception:
            pass
        time.sleep(5)
    return False


with st.form("deploy"):
    kaggle_username = st.text_input("Kaggle Username", placeholder="your_kaggle_username")
    kaggle_token = st.text_input("Kaggle API Token", type="password", placeholder="Kaggle API token")
    ngrok_token = st.text_input("ngrok Auth Token", type="password", placeholder="ngrok auth token")
    ngrok_domain = st.text_input("ngrok Domain / URL", placeholder="your-name.ngrok.app")
    start = st.form_submit_button("🚀 Start F5-TTS", use_container_width=True)


if start:
    username = kaggle_username.strip()
    ktoken = kaggle_token.strip()
    ntoken = ngrok_token.strip()
    domain = normalize_domain(ngrok_domain)

    if not username or not ktoken or not ntoken or not domain:
        st.error("Please fill all 4 fields.")
        st.stop()

    with st.spinner("Starting your personal F5-TTS server..."):
        ok, detail = verify_kaggle(username, ktoken)
        if not ok:
            st.error("Kaggle authentication failed. Please check your username and API token.")
            st.stop()

        folder = None
        try:
            folder, kernel_id = build_kernel_folder(username, ktoken, ntoken, domain)
            pushed = push_kernel(folder, username, ktoken)
            if pushed.returncode != 0:
                st.error("Kaggle could not start the F5-TTS server.")
                st.stop()

            ready = wait_for_public_url(domain, timeout=900)
            if not ready:
                st.error("F5-TTS did not become ready. Please try Start again.")
                st.stop()
        finally:
            if folder:
                shutil.rmtree(folder, ignore_errors=True)

    st.success("✅ Your F5-TTS server is ready")
    st.link_button("🎙️ Open F5-TTS Voice Clone / TTS", "https://" + domain, use_container_width=True)
