import logging
import requests
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVAC_MODE_COOL, HVAC_MODE_OFF
from homeassistant.const import TEMP_CELSIUS

_LOGGER = logging.getLogger(__name__)
DOMAIN = "cuby"

class CubyClimate(ClimateEntity):
    def __init__(self, name, token, device_id):
        self._name = name
        self._token = token
        self._device_id = device_id
        self._hvac_mode = HVAC_MODE_OFF
        self._temperature = 24  # Default temperature

    @property
    def name(self):
        return self._name

    @property
    def hvac_modes(self):
        return [HVAC_MODE_COOL, HVAC_MODE_OFF]

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def hvac_mode(self):
        return self._hvac_mode

    async def async_set_hvac_mode(self, hvac_mode):
        url = f"https://cuby.cloud/api/v2/devices/{self._device_id}/actions"
        payload = {"command": "set_mode", "value": hvac_mode.lower()}
        headers = {"Authorization": f"Bearer {self._token}"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            _LOGGER.info("Set HVAC mode to %s", hvac_mode)
            self._hvac_mode = hvac_mode
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error("Failed to set HVAC mode: %s", e)

    async def async_update(self):
        """Retrieve the current state of the A/C device."""
        url = f"https://cuby.cloud/api/v2/devices/{self._device_id}"
        headers = {"Authorization": f"Bearer {self._token}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self._temperature = data.get("current_temperature", 24)
            _LOGGER.info("Updated device temperature to %s", self._temperature)
        except Exception as e:
            _LOGGER.error("Failed to update device state: %s", e)