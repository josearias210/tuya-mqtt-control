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

   **Device configuration now uses individual environment variables for each device.**

   Example for two devices:
   ```env
   TUYA_DEVICES_0_ID=DEVICEID1
   TUYA_DEVICES_0_IP=192.168.1.10
   TUYA_DEVICES_0_KEY=KEY1

   TUYA_DEVICES_1_ID=DEVICEID2
   TUYA_DEVICES_1_IP=192.168.1.11
   TUYA_DEVICES_1_KEY=KEY2
   ```
   Add more devices by incrementing the index (0, 1, 2, ...).

   MQTT broker configuration:
   ```env
   MQTT_BROKER=mosquitto
   MQTT_PORT=1883
   ```

## Usage

Start the service:
```bash
python src/tuya_control.py
```

The service will connect to your MQTT broker and listen for commands.

## Docker Compose

A `docker-compose.yml` is provided for easy deployment. Make sure to set up your `.env` file as described above.

To build and run with Docker Compose:
```bash
docker compose up --build
```

## Testing

To run all tests:
```bash
python -m unittest discover tests
```

Or with pytest (install it first):
```bash
pip install pytest
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
