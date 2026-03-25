# Voice Recording & Webhook Response App

A Streamlit application that records user voice, sends it to a webhook, and plays back the response audio.

## Features

- Records voice using browser microphone (stops when user stops speaking)
- Sends the recording to a configurable webhook URL
- Waits for webhook response with audio file
- Plays the response audio automatically
- Option to download the response audio

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the webhook URL:
   - Edit `audio_listener_link.txt` and add your webhook URL
   - Example: `https://your-webhook-url.com/api/audio`

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Click the "Click to record" button to start recording
2. Speak into your microphone
3. Click "Stop recording" when done
4. Click "Send to Webhook and Get Response"
5. Wait for the webhook to process and respond
6. The response audio will automatically play

## Requirements

- Python 3.7+
- Streamlit
- Requests library
- A webhook endpoint that accepts audio files and returns audio responses
