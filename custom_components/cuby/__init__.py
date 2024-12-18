import logging
import requests
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

DOMAIN = "cuby"
TOKEN = None

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def get_auth_token(username, password):
    url = f"https://cuby.cloud/api/v2/token/{username}"
    payload = {"password": password, "expiration": 0}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        if token_data.get("status") == "ok":
            _LOGGER.info("Authentication successful.")
            return token_data["token"]
    except Exception as e:
        _LOGGER.error("Authentication failed: %s", e)
    return None

async def async_setup(hass, config):
    """Set up the Cuby component."""
    global TOKEN
    conf = config[DOMAIN]
    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]

    TOKEN = get_auth_token(username, password)
    if not TOKEN:
        _LOGGER.error("Failed to retrieve token. Check your credentials.")
        return False

    _LOGGER.info("Cuby integration successfully initialized.")
    hass.data[DOMAIN] = {"token": TOKEN}

    return True