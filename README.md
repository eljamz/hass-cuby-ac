# Cuby A/C Control Integration for Home Assistant

This custom integration allows Home Assistant to control **Cuby smart A/C devices** using their HTTP API.

## Installation

1. Install via **HACS**:
   - Add this repository (`https://github.com/yourusername/cuby-home-assistant`) as a custom repository in HACS.
   - Search for "Cuby A/C Control" and install.

2. Restart Home Assistant.

3. Add the following to your `configuration.yaml`:

```yaml
cuby:
  username: "email@here.com"
  password: "your_password"
  expiration: 0