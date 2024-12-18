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

PLATFORMS = [Platform.CLIMATE]

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