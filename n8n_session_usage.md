# Using Session ID in n8n

## How It Works

The Streamlit app now sends a unique `session_id` with every audio request. This ID:
- Is automatically generated on first load using UUID v4
- Persists throughout the browser session
- Can be reset by clicking "New Conversation"
- Is sent as form data alongside the audio file

## Accessing Session ID in n8n

The session ID is sent as form data in the POST request. In your n8n workflow:

### Method 1: Direct Access (Recommended)
```javascript
{{ $json.session_id }}
```

### Method 2: From Body
```javascript
{{ $('Webhook').item.json.body.session_id }}
```

## Example n8n Usage

### 1. Store Session ID in Variable
Create a "Set" node after the Webhook:
```
Name: session_id
Value: {{ $json.session_id }}
```

### 2. Use for Memory/Database Lookup
In a database query node:
```sql
SELECT * FROM conversations WHERE session_id = '{{ $json.session_id }}'
```

### 3. Include in AI Context
If using an AI node, include it in the prompt:
```
Conversation ID: {{ $json.session_id }}
Previous context: [fetch from database using session_id]
User audio: [transcribed audio]
```

### 4. Store New Messages
When saving conversation history:
```javascript
{
  "session_id": "{{ $json.session_id }}",
  "timestamp": "{{ $now }}",
  "user_message": "{{ $json.transcription }}",
  "ai_response": "{{ $json.ai_reply }}"
}
```

## Example Workflow Structure

1. **Webhook Node** - Receives audio + session_id
2. **Extract Session ID** - Store in variable
3. **Check if Session Exists** - Query database/memory
4. **Load Context** - Get previous conversation if exists
5. **Process Audio** - Transcribe
6. **Generate Response** - Use AI with context
7. **Save to Memory** - Store with session_id
8. **Return Audio** - Send response back

## Testing

The app displays a shortened session ID at the top (e.g., "Session ID: a1b2c3d4...").

To test:
1. Record and send audio
2. In n8n, check the webhook data to see the full session_id
3. Record another message - it should have the same session_id
4. Click "New Conversation" - next message will have a different session_id

## Session ID Format

- Format: UUID v4 (e.g., `a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6`)
- Length: 36 characters
- Uniqueness: Virtually guaranteed unique across all sessions
