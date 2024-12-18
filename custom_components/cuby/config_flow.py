"""Config flow for Cuby integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN, CubyAPI, CONF_EXPIRATION

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_EXPIRATION, default=0): vol.All(
        vol.Coerce(int),
        vol.Range(min=0)
    ),
})

class CubyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cuby."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                api = CubyAPI(
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input.get(CONF_EXPIRATION, 0)
                )

                if await api.authenticate():
                    # Check if we can get the device list
                    devices = await api.get_devices()
                    if not devices:
                        errors["base"] = "no_devices"
                    else:
                        await self.async_set_unique_id(user_input[CONF_USERNAME])
                        self._abort_if_unique_id_configured()
                        
                        return self.async_create_entry(
                            title=user_input[CONF_USERNAME],
                            data=user_input,
                        )
                else:
                    errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        ) 