"""
==================================================
Author: Jan Nalepka
Script version: 1.0
Date: 19.11.2025
Repository: https://github.com/jnalepka/homeassistant-to-grenton
==================================================
"""

from homeassistant import config_entries
import voluptuous as vol
from .options_flow import GrentonWatcherOptionsFlowHandler
from homeassistant.core import callback

DOMAIN = "grenton_watcher"

class GrentonWatcherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._persist_last_inputs(user_input)
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "api_endpoint": user_input["api_endpoint"],
                },
            )
        
        default_url = self.hass.data.get(f"{DOMAIN}_last_api_endpoint", "http://192.168.0.4/HAlistener")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("api_endpoint", default=default_url): str,
            }),
        )
        
    def _persist_last_inputs(self, user_input: dict) -> None:
        self.hass.data[f"{DOMAIN}_last_api_endpoint"] = user_input["api_endpoint"]
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> GrentonWatcherOptionsFlowHandler:
        return GrentonWatcherOptionsFlowHandler()