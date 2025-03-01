# Virtual Assistant

This is a customizable virtual assistant powered by ChatGPT. You can set up your own assistant with a unique personality, voice, and wake word. It supports multiple assistants running simultaneously and allows you to write custom Python functions that the assistant can call when needed.

## Features
- **Custom Personalities & Voices**: Define different assistants with unique behaviors.
- **Multiple Assistants**: Run multiple assistants at the same time.
- **Python Function Calls**: Extend the assistant's capabilities by writing custom functions.
- **Home Assistant Integration**: Automatically detects devices and services.
- **Twilio Integration**: Call the assistant and talk to it over the phone.
- **Web GUI**: Interact with the assistant and configure settings through a web interface.
- **Multi-Language Support**: Communicate in different languages.
- **Easy Setup**: Simple installation process.

## Installation
### Using Python
```sh
# Clone the repository
git clone https://github.com/bearmanser/MagnusAssistant
cd MagnusAssistant

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the assistant
python main.py
```

### Using Docker
```sh
git clone https://github.com/bearmanser/MagnusAssistant
cd MagnusAssistant

docker-compose up --build
```

## Twilio Setup (Optional)
To enable Twilio phone call support, follow these steps:
1. **Sign up** on [Twilio Console](https://www.twilio.com/console) and obtain your **Account SID** and **Auth Token**.
2. **Set up a TwiML Bin** in the Twilio Console with the following XML:
```xml
<Response>
  <Play>https://your-server-url/greeting</Play>
  <Start>
    <Stream url="wss://your-server-url/stream">
      <Parameter name="callSid" value="{{CallSid}}" />
    </Stream>
  </Start>
  <Pause length="3600"/>
</Response>
```
3. **Configure Twilio Settings in the Web GUI**:
   - Set the **Base URL** (e.g., `https://your-server-url`).
   - Enter the **Twilio Account SID** and **Auth Token**.
   - Select which assistant should answer calls.

## Home Assistant Integration
Set the following environment variables to enable Home Assistant integration:
```sh
export HOME_ASSISTANT_URL="http://your-home-assistant.local:8123"
export HOME_ASSISTANT_TOKEN="your-home-assistant-token"
```
Or in a `.env` file:
```
HOME_ASSISTANT_URL=http://your-home-assistant.local:8123
HOME_ASSISTANT_TOKEN=your-home-assistant-token
```

## Usage
The web GUI will start with the server and run on port 3000.
Once running, access the web GUI to configure settings and interact with the assistant.

## License
[Apache 2.0 License](LICENSE)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your idea.

