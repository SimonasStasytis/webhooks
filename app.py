import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
import uuid
 
def get_webhook_url():
    """Read the webhook URL from Streamlit secrets or fallback to file"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["WEBHOOK_URL"]
    except (KeyError, FileNotFoundError):
        pass
 
    # Fallback: read from local file (for local development)
    try:
        with open("audio_listener_link.txt", "r") as f:
            url = f.read().strip()
        if url.startswith("http://localhost"):
            st.warning(
                "⚠️ Your webhook URL points to `localhost` — this won't work on Streamlit Cloud. "
                "Add your real webhook URL in **App Settings → Secrets** as `WEBHOOK_URL`.",
                icon="⚠️",
            )
            return None
        return url
    except FileNotFoundError:
        st.error("No webhook URL found. Add `WEBHOOK_URL` to your Streamlit secrets.")
        return None
 
 
def send_audio_to_webhook(audio_data, webhook_url, session_id):
    """Send audio data to the webhook and return the response"""
    try:
        files = {"audio": ("recording.wav", audio_data, "audio/wav")}
        data = {"session_id": session_id}
        response = requests.post(webhook_url, files=files, data=data, timeout=120)
 
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Webhook returned status code {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {str(e)}")
        return None
 
 
def autoplay_audio(audio_bytes):
    """Auto-play audio using an HTML5 audio element"""
    b64 = base64.b64encode(audio_bytes).decode()
    audio_id = f"audio_{uuid.uuid4().hex}"
    html_string = f"""
        <audio id="{audio_id}" autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        <script>
            document.getElementById('{audio_id}').play();
        </script>
    """
    components.html(html_string, height=0)
 
 
# ── App ──────────────────────────────────────────────────────────────────────
 
st.title("Voice Recording & Webhook Response")
 
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "response_count" not in st.session_state:
    st.session_state.response_count = 0
 
webhook_url = get_webhook_url()
 
if webhook_url:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
    with col2:
        if st.button("New Conversation"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.last_audio_id = None
            st.session_state.response_count = 0
            st.rerun()
 
    st.divider()
 
    audio_data = st.audio_input("Record your voice")
 
    if audio_data is not None:
        audio_id = hash(audio_data.getvalue())
        st.audio(audio_data, format="audio/wav")
 
        if st.session_state.last_audio_id != audio_id:
            st.session_state.last_audio_id = audio_id
 
            with st.spinner("Processing… waiting for response"):
                response_audio = send_audio_to_webhook(
                    audio_data, webhook_url, st.session_state.session_id
                )
 
            if response_audio:
                st.session_state.response_count += 1
                st.success("Response received!")
                autoplay_audio(response_audio)