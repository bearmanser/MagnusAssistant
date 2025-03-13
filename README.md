# Virtual Assistant

This is a customizable virtual assistant powered by ChatGPT. You can set up your own assistant with a unique personality, voice, and wake word. It supports multiple assistants running simultaneously and allows you to write custom Python functions that the assistant can call when needed. You can even call or text the assistant over the phone.

## Features
- **Custom Personalities & Voices**: Define different assistants with unique behaviors.
- **Multiple Assistants**: Run multiple assistants at the same time.
- **Python Function Calls**: Extend the assistant's capabilities by writing custom functions.
- **Home Assistant Integration**: Automatically detects devices and services.
- **Twilio Integration**: Call or send SMS messages to the assistant.
- **Web GUI**: Interact with the assistant and configure settings through a web interface.
- **Multi-Language Support**: Communicate in different languages.
- **Easy Setup**: Quick and straightforward installation.



## Installation
  
> **An NVIDIA GPU with CUDA support (Compute Capability X.X or higher) is required. Most recent NVIDIA GPUs support this, but other GPU brands are not compatible. You must also have the appropriate NVIDIA driver installed for CUDA to function properly. Download the latest drivers from [NVIDIA's official website](https://www.nvidia.com/en-us/drivers/). Additionally, the NVIDIA Container Toolkit must be installed. Follow the installation guide at [NVIDIA Container Toolkit Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).**

### Using Python
> **Requirements**: Python **3.10** is required.

```sh
# Clone the repository
git clone https://github.com/bearmanser/MagnusAssistant
cd MagnusAssistant

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run the assistant
python3 main.py
```

### Using Docker
```sh
git clone https://github.com/bearmanser/MagnusAssistant
cd MagnusAssistant

docker-compose up -d --build
```

## Twilio Setup
To enable Twilio phone call and SMS support, follow these steps:

1. **Sign up** on [Twilio Console](https://www.twilio.com/console) and obtain your **Account SID** and **Auth Token**.
2. **Set up a TwiML Bin** in the Twilio Console with the following XML:
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
3. Go to **Phone Numbers** → **Manage** → **Active Numbers**, then configure your number to use the TwiML App.
4. Under **Messaging Configuration**, set the webhook for "A message comes in" to:
   ```
   https://your-server-url:3003/sms-webhook
   ```
5. **Configure Twilio Settings in the Web GUI**:
   - Set the **Base URL** (e.g., `https://your-server-url:3003`).
   - Enter the **Twilio Account SID** and **Auth Token**.
   - Select which assistant should answer calls and SMS messages.

> **Note:** The `your-server-url` must be an externally accessible domain (not `localhost`), or use a tunneling service like **ngrok** for local development.

## Home Assistant Integration
Set the following environment variables to enable Home Assistant integration:

```sh
export HOME_ASSISTANT_URL="http://your-home-assistant.local:8123"
export HOME_ASSISTANT_TOKEN="your-home-assistant-token"
```
Or in docker-compose.yaml:
```yaml
services:
  virtual-assistant:
    environment:
      - HOME_ASSISTANT_URL=http://your-home-assistant.local:8123     #Edit these fields
      - HOME_ASSISTANT_TOKEN=your-home-assistant-token               #Edit these fields
```

## Usage
The web GUI starts automatically with the server and runs on port `3000`.  
Once running, access the interface at **[http://localhost:3000](http://localhost:3000)** (or your server's IP if running remotely).  

## License
This project is licensed under the **Apache 2.0 License**. See [LICENSE](LICENSE) for details.


[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/oddmagnusgrinder)
