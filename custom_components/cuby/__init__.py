"""The Cuby A/C Control integration."""
import logging
import asyncio
import aiohttp
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    Platform,
)
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "cuby"
CONF_EXPIRATION = "expiration"

PLATFORMS = [Platform.CLIMATE, Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_EXPIRATION, default=0): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

class CubyAPI:
    """Cuby API client."""

    def __init__(self, username: str, password: str, expiration: int = 0):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.expiration = expiration
        self.token = None
        self._session = None

    async def authenticate(self) -> bool:
        """Authenticate with the Cuby API."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        try:
            url = f"https://cuby.cloud/api/v2/token/{self.username}"
            payload = {
                "password": self.password,
                "expiration": self.expiration
            }

            async with self._session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "ok":
                        self.token = data.get("token")
                        return True
                return False
        except Exception as err:
            _LOGGER.error("Error authenticating with Cuby API: %s", err)
            return False

    async def get_devices(self) -> list:
        """Get list of Cuby devices."""
        if not self.token:
            if not await self.authenticate():
                return []

        try:
            url = "https://cuby.cloud/api/v2/devices"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as err:
            _LOGGER.error("Error getting devices: %s", err)
            return []

    async def get_device_state(self, device_id: str) -> dict:
        """Get the current state of a device."""
        if not self.token:
            if not await self.authenticate():
                return {}

        try:
            url = f"https://cuby.cloud/api/v2/devices/{device_id}/state"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting device state: %s", err)
            return {}

    async def set_device_state(self, device_id: str, state: dict) -> bool:
        """Set the state of a device."""
        if not self.token:
            if not await self.authenticate():
                return False

        try:
            url = f"https://cuby.cloud/api/v2/devices/{device_id}/state"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self._session.post(url, headers=headers, json=state) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error("Error setting device state: %s", err)
            return False

    async def discover_devices(self) -> list:
        """Discover and return all available devices."""
        devices = await self.get_devices()
        discovered = []
        
        for device in devices:
            try:
                state = await self.get_device_state(device["id"])
                device["state"] = state
                discovered.append(device)
            except Exception as err:
                _LOGGER.error("Error discovering device %s: %s", device.get("id"), err)
                
        return discovered

    async def get_device_info(self, device_id: str) -> dict:
        """Get detailed device information."""
        if not self.token:
            if not await self.authenticate():
                return {}

        try:
            url = f"https://cuby.cloud/api/v2/devices/{device_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with self._session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting device info: %s", err)
            return {}

    async def set_ac_power(self, device_id: str, power: bool) -> bool:
        """Turn the AC on or off."""
        return await self.set_device_state(device_id, {"power": power})

    async def set_ac_temperature(self, device_id: str, temperature: float) -> bool:
        """Set the target temperature."""
        # Ensure temperature is within valid range (16-30°C)
        temp = min(max(temperature, 16), 30)
        return await self.set_device_state(device_id, {"temperature": temp})

    async def set_ac_mode(self, device_id: str, mode: str) -> bool:
        """Set the AC operation mode."""
        valid_modes = ["auto", "cool", "heat", "dry", "fan_only"]
        if mode not in valid_modes:
            _LOGGER.error("Invalid mode: %s. Must be one of %s", mode, valid_modes)
            return False
        return await self.set_device_state(device_id, {"mode": mode})

    async def set_ac_fan_mode(self, device_id: str, fan_mode: str) -> bool:
        """Set the fan mode."""
        valid_fan_modes = ["auto", "low", "medium", "high"]
        if fan_mode not in valid_fan_modes:
            _LOGGER.error("Invalid fan mode: %s. Must be one of %s", fan_mode, valid_fan_modes)
            return False
        return await self.set_device_state(device_id, {"fan_mode": fan_mode})

    async def set_ac_swing_mode(self, device_id: str, swing_mode: str) -> bool:
        """Set the swing mode."""
        valid_swing_modes = ["off", "vertical", "horizontal", "both"]
        if swing_mode not in valid_swing_modes:
            _LOGGER.error("Invalid swing mode: %s. Must be one of %s", swing_mode, valid_swing_modes)
            return False
        return await self.set_device_state(device_id, {"swing": swing_mode})

    async def set_ac_full_state(self, device_id: str, state: dict) -> bool:
        """Set multiple AC parameters at once."""
        valid_keys = {"power", "temperature", "mode", "fan_mode", "swing"}
        filtered_state = {k: v for k, v in state.items() if k in valid_keys}
        
        if not filtered_state:
            _LOGGER.error("No valid parameters provided")
            return False
            
        return await self.set_device_state(device_id, filtered_state)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Cuby component."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    expiration = conf[CONF_EXPIRATION]

    api = CubyAPI(username, password, expiration)
    if not await api.authenticate():
        _LOGGER.error("Failed to authenticate with Cuby API")
        return False

    hass.data[DOMAIN] = api

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(platform, DOMAIN, {}, config)
        )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cuby from a config entry."""
    # TODO: Implement config flow setup
    return True