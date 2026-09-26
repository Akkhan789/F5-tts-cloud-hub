import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

st.set_page_config(page_title="F5-TTS Personal Server", page_icon="🎙️", layout="centered")

st.title("🎙️ F5-TTS Personal Server")
st.caption("Pehle Kaggle aur ngrok ko alag-alag verify karein, phir F5-TTS start karein.")


def normalize_domain(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    parsed = urlparse(value)
    return parsed.netloc.lower().strip().rstrip("/")


def classify_kaggle_error(text: str) -> str:
    s = (text or "").lower()
    if "401" in s or "unauthorized" in s or "authentication" in s or "invalid credentials" in s:
        return "Kaggle authentication failed: username/API token invalid or expired."
    if "403" in s or "forbidden" in s or "permission" in s:
        return "Kaggle permission denied: this account/token cannot access the requested API action."
    if "429" in s or "rate limit" in s:
        return "Kaggle rate limit reached. Please wait and try again."
    if "not found" in s or "404" in s:
        return "Kaggle resource/account was not found. Check the username."
    return "Kaggle verification failed. See the technical error below."


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
            timeout=30,
        )
        raw = (result.stderr or result.stdout or "").strip()
        if result.returncode == 0:
            return True, "Kaggle API authentication successful."
        return False, classify_kaggle_error(raw) + "\n\n" + raw[-2500:]
    except FileNotFoundError:
        return False, "Kaggle CLI is not installed on the Streamlit server. Add kaggle to requirements.txt."
    except subprocess.TimeoutExpired:
        return False, "Kaggle verification timed out after 30 seconds."
    except Exception as exc:
        return False, f"Kaggle verification error: {exc}"


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"ngrok verification server"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def classify_ngrok_error(text: str) -> str:
    s = (text or "").lower()
    if "authentication failed" in s or "invalid authtoken" in s or "authtoken" in s and "invalid" in s:
        return "ngrok Auth Token problem: token invalid, revoked, or not accepted by ngrok."
    if "authorization failed" in s or "unauthorized" in s or "401" in s:
        return "ngrok authentication problem: Auth Token was rejected."
    if "domain" in s and ("not found" in s or "does not exist" in s or "not exist" in s):
        return "ngrok Domain problem: this domain is not available in the ngrok account."
    if "already online" in s or "already in use" in s or "endpoint already" in s:
        return "ngrok Domain problem: this domain is already being used by another active endpoint."
    if "forbidden" in s or "403" in s or "not authorized" in s:
        return "ngrok Domain permission problem: this account/token cannot bind this domain."
    if "reserved" in s or "custom domain" in s or "plan" in s or "upgrade" in s:
        return "ngrok Domain/plan problem: this domain or feature may not be enabled for this account."
    if "connect" in s or "network" in s or "dial" in s:
        return "ngrok network problem: the Streamlit server could not connect to ngrok."
    return "ngrok verification failed. See the technical error below."


def verify_ngrok(auth_token: str, domain: str):
    """Actually start a short-lived ngrok tunnel to verify token + domain together."""
    server = None
    tunnel = None
    try:
        from pyngrok import ngrok
        from pyngrok.conf import PyngrokConfig

        server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        local_port = server.server_address[1]

        cfg = PyngrokConfig(auth_token=auth_token.strip())
        tunnel = ngrok.connect(local_port, proto="http", domain=domain, pyngrok_config=cfg)
        public_url = tunnel.public_url
        return True, f"ngrok Auth Token + Domain verified successfully.\nEndpoint: {public_url}"
    except Exception as exc:
        raw = str(exc)
        return False, classify_ngrok_error(raw) + "\n\n" + raw[-3500:]
    finally:
        try:
            from pyngrok import ngrok
            ngrok.kill()
        except Exception:
            pass
        if server:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass


def build_kernel_folder(username: str, ngrok_token: str, domain: str):
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
    (folder / "f5tts_server.py").write_text(node_code, encoding="utf-8")
    metadata = {
        "id": f"{username.strip()}/{slug}",
        "title": title,
        "code_file": "f5tts_server.py",
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
    """Return True only when the actual F5-TTS/Gradio page is HTTP 200.

    Important: an offline ngrok endpoint can return an HTTP error page (for
    example ERR_NGROK_3200). Treating any 2xx-4xx response as ready caused
    false "server is ready" messages.
    """
    url = "https://" + domain.rstrip("/") + "/"
    started = time.time()
    while time.time() - started < timeout:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "F5-TTS-Ready-Check"},
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                body = response.read(30000).decode("utf-8", errors="ignore")
                lower = body.lower()
                # Only HTTP 200 from the real upstream counts as ready.
                # ngrok error pages must never be accepted as readiness.
                if (
                    response.status == 200
                    and "err_ngrok_" not in lower
                    and "endpoint is offline" not in lower
                ):
                    return True
        except urllib.error.HTTPError:
            # 404/502/etc. means the public endpoint is not ready yet.
            pass
        except Exception:
            pass
        time.sleep(5)
    return False


# ------------------------- UI -------------------------

if "kaggle_verified" not in st.session_state:
    st.session_state.kaggle_verified = False
if "ngrok_verified" not in st.session_state:
    st.session_state.ngrok_verified = False

st.subheader("1. Kaggle")
kaggle_username = st.text_input("Kaggle Username", placeholder="your_kaggle_username", key="kaggle_username")
kaggle_token = st.text_input("Kaggle API Token", type="password", placeholder="Kaggle API token", key="kaggle_token")

if st.button("🔐 Verify Kaggle", use_container_width=True):
    if not kaggle_username.strip() or not kaggle_token.strip():
        st.error("Kaggle Username aur API Token dono enter karein.")
    else:
        with st.spinner("Kaggle credentials verify ho rahe hain..."):
            ok, message = verify_kaggle(kaggle_username, kaggle_token)
        st.session_state.kaggle_verified = ok
        if ok:
            st.success("✅ " + message)
        else:
            st.error("❌ " + message.split("\n\n")[0])
            with st.expander("Technical error"):
                st.code(message)

if st.session_state.kaggle_verified:
    st.caption("🟢 Kaggle verified")

st.subheader("2. ngrok")
ngrok_token = st.text_input("ngrok Auth Token", type="password", placeholder="ngrok auth token", key="ngrok_token")
ngrok_domain_input = st.text_input("ngrok Domain / URL", placeholder="your-name.ngrok.app", key="ngrok_domain")

if st.button("🔐 Verify ngrok", use_container_width=True):
    domain = normalize_domain(ngrok_domain_input)
    if not ngrok_token.strip() or not domain:
        st.error("ngrok Auth Token aur Domain dono enter karein.")
    else:
        with st.spinner("ngrok Auth Token + Domain verify ho rahe hain..."):
            ok, message = verify_ngrok(ngrok_token, domain)
        st.session_state.ngrok_verified = ok
        if ok:
            st.success("✅ " + message.split("\n")[0])
            if "Endpoint:" in message:
                st.caption(message.split("Endpoint:", 1)[1].strip())
        else:
            st.error("❌ " + message.split("\n\n")[0])
            with st.expander("Technical error"):
                st.code(message)

if st.session_state.ngrok_verified:
    st.caption("🟢 ngrok verified")

st.divider()

if st.button("🚀 Start F5-TTS", type="primary", use_container_width=True):
    username = kaggle_username.strip()
    ktoken = kaggle_token.strip()
    ntoken = ngrok_token.strip()
    domain = normalize_domain(ngrok_domain_input)

    if not username or not ktoken or not ntoken or not domain:
        st.error("Pehle tamam 4 details enter karein.")
        st.stop()

    if not st.session_state.kaggle_verified:
        st.error("Pehle 'Verify Kaggle' successful hona zaroori hai.")
        st.stop()

    if not st.session_state.ngrok_verified:
        st.error("Pehle 'Verify ngrok' successful hona zaroori hai.")
        st.stop()

    with st.spinner("F5-TTS server start ho raha hai. Please wait..."):
        folder = None
        try:
            folder, kernel_id = build_kernel_folder(username, ntoken, domain)
            pushed = push_kernel(folder, username, ktoken)
            if pushed.returncode != 0:
                raw = (pushed.stderr or pushed.stdout or "").strip()
                st.error("Kaggle kernel start nahi ho saka.")
                with st.expander("Technical error"):
                    st.code(raw[-5000:] or "No error text returned by Kaggle.")
                st.stop()

            ready = wait_for_public_url(domain, timeout=900)
            if not ready:
                st.error("F5-TTS server 15 minutes ke andar ready nahi hua. Verify buttons se Kaggle/ngrok dobara check karein.")
                st.stop()
        finally:
            if folder:
                shutil.rmtree(folder, ignore_errors=True)

    st.success("✅ Your F5-TTS server is ready")
    st.link_button("🎙️ Open F5-TTS Voice Clone / TTS", "https://" + domain, use_container_width=True)
