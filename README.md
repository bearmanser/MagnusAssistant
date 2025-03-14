# Virtual Assistant

A customizable virtual assistant powered by ChatGPT. Define assistants with unique personalities, voices, and wake words. Supports multiple simultaneous assistants, custom Python functions, Home Assistant integration, and phone/SMS interactions via Twilio.

## Features
- **Custom Personalities & Voices**: Unique assistant behaviors.
- **Multiple Assistants**: Run concurrently.
- **Python Function Calls**: Extend capabilities via Python.
- **Home Assistant Integration**: Automatic device/service detection.
- **Twilio Integration**: Enable calls/SMS with the assistant.
- **Web GUI**: Easy interaction and configuration.
- **Multi-Language Support**: Supports various languages.
- **Easy Setup**: Quick and simple installation.

## Quick Start Guide

### Prerequisites
- **NVIDIA GPU with CUDA support**.
- Latest NVIDIA drivers ([NVIDIA Drivers](https://www.nvidia.com/en-us/drivers/)).
- NVIDIA Container Toolkit ([Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)).
- Docker and Docker Compose.

> **Note:** If you're using WSL, you must install the GPU driver in Windows and the toolkit in WSL.

### Installation
```bash
git clone https://github.com/bearmanser/MagnusAssistant
cd MagnusAssistant

docker-compose up -d --build
```

### Initial Configuration
1. Open the Web GUI at [http://localhost:3000](http://localhost:3000).
2. Navigate to **Settings** and configure:
   - **OpenAI API Key**.
   - **Twilio** (Account SID, Auth Token, and Base URL).
3. Under **Assistant Configuration**, define your assistant(s) or use the default.
4. Optionally, configure custom Python functions under **Custom Commands**. You can create virtually any Python function, and the assistant will automatically understand and utilize it appropriately, enabling integration with almost any service or API.

### Interacting with the Assistant
Use the **Interface** tab to speak with your assistant. Say the wake word (default is **"Magnus"**) to begin interaction.

## Twilio Setup (Optional)
Enable phone and SMS support:

1. [Sign up on Twilio](https://www.twilio.com/console) and get your Account SID and Auth Token.
2. Navigate to **TwiML Bins** and create a new TwiML Bin with the following XML:
```xml
<Response>
  <Play>https://your-server-url:3003/greeting</Play>
  <Start>
    <Stream url="wss://your-server-url:3003/stream">
      <Parameter name="callSid" value="{{CallSid}}" />
    </Stream>
  </Start>
  <Pause length="3600"/>
</Response>
```
3. Go to **Phone Numbers** → **Manage** → **Active Numbers**, select your phone number, and set it to use the TwiML Bin created above.
4. Under **Messaging Configuration**, set the webhook for incoming messages to:
   ```
   https://your-server-url:3003/sms-webhook
   ```
   > **Note:** The `your-server-url` must be an externally accessible domain (not `localhost`), or use a tunneling service like **ngrok** for local development.
5. In the Virtual Assistant Web GUI, ensure the **Base URL**, **Twilio Account SID**, and **Auth Token** are configured correctly.

## Home Assistant Integration (Optional)
Configure via environment variables in `docker-compose.yaml`:
```yaml
services:
  virtual-assistant:
    environment:
      - HOME_ASSISTANT_URL=http://your-home-assistant.local:8123
      - HOME_ASSISTANT_TOKEN=your-home-assistant-token
```

## License
Licensed under the [Apache 2.0 License](LICENSE).

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/oddmagnusgrinder)

