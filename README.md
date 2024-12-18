# Cuby A/C Control Integration for Home Assistant

This custom integration allows Home Assistant to control **Cuby smart A/C devices** using their HTTP API.

## Installation

1. Install via **HACS**:
   - Add this repository (`https://github.com/eljamz/hass-cuby-ac`) as a custom repository in HACS.
   - Search for "Cuby A/C Control" and install.

2. Restart Home Assistant.

3. Go to Settings -> Devices & Services
4. Click "Add Integration"
5. Search for "Cuby A/C Control"
6. Enter your credentials:
   - Email: Your Cuby account email
   - Password: Your Cuby account password
   - Token Expiration: (Optional) Token expiration time in seconds

## Features

- Control A/C power (on/off)
- Set temperature
- Change operation mode (auto, cool, heat, dry, fan only)
- Control fan speed
- Monitor device status
- View WiFi signal strength
- Check online status

## Troubleshooting

If you encounter any issues:
1. Check your credentials
2. Ensure your Cuby devices are online
3. Check the Home Assistant logs for detailed error messages
