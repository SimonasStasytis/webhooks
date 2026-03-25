import streamlit as st
import streamlit.components.v1 as components
import requests
import base64
import uuid

# Read the webhook URL from file
def get_webhook_url():
    """Read the webhook URL from audio_listener_link.txt"""
    try:
        with open("audio_listener_link.txt", "r") as f:
            url = f.read().strip()
        return url
    except FileNotFoundError:
        st.error("Error: audio_listener_link.txt file not found.")
        return None

def send_audio_to_webhook(audio_data, webhook_url, session_id):
    """Send audio data to the webhook and return the response"""
    try:
        # Prepare the file for upload and include session_id
        files = {"audio": ("recording.wav", audio_data, "audio/wav")}
        data = {"session_id": session_id}
        
        # Send POST request to the webhook and wait for response
        response = requests.post(webhook_url, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            # Return the audio content from the response
            return response.content
        else:
            st.error(f"Error: Webhook returned status code {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {str(e)}")
        return None

def autoplay_audio(audio_bytes):
    """Auto-play audio using HTML5 audio element with components"""
    b64 = base64.b64encode(audio_bytes).decode()
    # Create a unique identifier to force new element
    audio_id = f"audio_{uuid.uuid4().hex}"
    
    html_string = f"""
        <audio id="{audio_id}" autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        <script>
            var audio = document.getElementById('{audio_id}');
            audio.play();
        </script>
        """
    
    components.html(html_string, height=0)

# Streamlit App
st.title("Voice Recording & Webhook Response")

# Initialize session ID if it doesn't exist
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize tracking for processed audio
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

# Initialize response counter
if "response_count" not in st.session_state:
    st.session_state.response_count = 0

# Get webhook URL
webhook_url = get_webhook_url()

if webhook_url:
    # Show session info and new conversation button
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
    
    # Audio input widget
    audio_data = st.audio_input("Record your voice")
    
    if audio_data is not None:
        # Create a unique ID for this audio recording
        audio_id = hash(audio_data.getvalue())
        
        # Show the recorded audio
        st.audio(audio_data, format="audio/wav")
        
        # Only process if this is a new recording
        if st.session_state.last_audio_id != audio_id:
            # Update the last processed audio ID
            st.session_state.last_audio_id = audio_id
            
            # Automatically send to webhook when recording stops
            with st.spinner("Processing... waiting for response"):
                # Send audio to webhook and wait for response
                response_audio = send_audio_to_webhook(audio_data, webhook_url, st.session_state.session_id)
                
                if response_audio:
                    # Increment counter for unique rendering
                    st.session_state.response_count += 1
                    st.success("Response received!")
                    # Play the audio immediately
                    autoplay_audio(response_audio)
else:
    st.warning("Please create the audio_listener_link.txt file with your webhook URL.")
