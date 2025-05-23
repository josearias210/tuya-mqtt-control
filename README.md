[![Build and Release Docker Image](https://github.com/josearias210/tuya-mqtt-control/actions/workflows/docker-build-release.yml/badge.svg)](https://github.com/josearias210/tuya-mqtt-control/actions/workflows/docker-build-release.yml)

# Tuya MQTT Control

A simple Python service to control Tuya Smart Bulbs via MQTT.
Easily integrate your Tuya bulbs with any MQTT-compatible home automation system.

## Features

- Turn Tuya bulbs on/off via MQTT
- Set brightness and color (RGB/HSV or color names)
- Query real-time device status
- Supports multiple bulbs
- Easy configuration via environment variables

## Requirements

- Python 3.7+
- [tinytuya](https://github.com/jasonacox/tinytuya)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/)
- Tuya bulbs with local key and IP address

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/josearias210/tuya-mqtt-control.git
   cd tuya-mqtt-control
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy and edit the environment file:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your Tuya device info and MQTT broker settings.

## Usage

Start the service:
```bash
python tuya_control.py
```

The service will connect to your MQTT broker and listen for commands.

## MQTT Topics

- `/device/<device_id>/light/on` — Turn bulb ON (payload ignored)
- `/device/<device_id>/light/off` — Turn bulb OFF (payload ignored)
- `/device/<device_id>/light/brightness` — Set brightness (payload: 0-255)
- `/device/<device_id>/light/color` — Set color (payload: color name or JSON with RGB/HSV)
- `/device/<device_id>/light/status/request` — Request status update (payload ignored)
- `/device/<device_id>/light/status` — Device publishes status here (JSON)

## Environment Variables

The application uses a `.env` file for configuration. Example variables:

```
TUYA_DEVICES=[{"id": "dev1", "ip": "192.168.1.10", "key": "abc123"}]
MQTT_BROKER=mosquitto
MQTT_PORT=1883
```

See `.env.example` for a template you can copy and edit.

## Example MQTT Commands

Turn on a bulb:
```bash
mosquitto_pub -t "/device/dev1/light/on" -m ""
```

Set brightness:
```bash
mosquitto_pub -t "/device/dev1/light/brightness" -m "128"
```

Set color (red):
```bash
mosquitto_pub -t "/device/dev1/light/color" -m "red"
```

Set color (RGB):
```bash
mosquitto_pub -t "/device/dev1/light/color" -m '{"r":255,"g":100,"b":50}'
```

## Running Tests

To run the test suite, make sure you have all dependencies installed (see [Installation](#installation)).

You can run the tests using Python's built-in unittest (default):

**With unittest:**
```bash
python -m unittest discover tests
```

If you prefer to use pytest, first install it with:
```bash
pip install pytest
```
Then run:
```bash
pytest
```

Both commands will automatically discover and run all tests in the `tests/` directory.

## CI/CD Workflow and Docker Image

This project uses a single GitHub Actions workflow for both build and release:

- **Build:** On every push, pull request, or manual trigger, the workflow installs dependencies, runs tests, and builds the Docker image for validation.
- **Release:** When a commit is pushed to `master` or a tag is created, the workflow also publishes a multi-architecture Docker image (for x64 and ARM64, compatible with Raspberry Pi 5) to GitHub Container Registry (ghcr.io).
- The image is tagged as `latest` and with the version (from the tag or as `x.x.x`).

### Pulling the Docker Image

You can pull the published image with:

```bash
docker pull ghcr.io/josearias210/tuya-mqtt-control:latest
```
Or for a specific version (replace `<version>` with the tag):
```bash
docker pull ghcr.io/josearias210/tuya-mqtt-control:<version>
```

The image supports both `linux/amd64` (PC/Server) and `linux/arm64` (Raspberry Pi 5, etc).

For more details, see the [GitHub Packages page](https://github.com/users/josearias210/packages/container/package/tuya-mqtt-control).

## Contributing

Pull requests and issues are welcome!
Please open an issue for bugs or feature requests.

## License

MIT License

---

## **Disclaimer:**

This is an independent, hobby project and is not affiliated with, endorsed by, or supported by Tuya or any official entity. The software is provided as-is, with no guarantees of stability or fitness for any particular purpose. Use at your own risk. The author assumes no responsibility for any issues, damages, or consequences resulting from its use. This project is under active development and may change at any time.
