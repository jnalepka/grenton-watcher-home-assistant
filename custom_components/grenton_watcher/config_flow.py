from homeassistant import config_entries
import voluptuous as vol
from .options_flow import GrentonWatcherOptionsFlowHandler

DOMAIN = "grenton_watcher"

class GrentonWatcherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._persist_last_inputs(user_input)
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "url": user_input["url"],
                },
            )
        
        default_url = self.hass.data.get(f"{DOMAIN}_last_url", "http://192.168.0.4/HAlistener")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("url", default=default_url): str,
            }),
        )
        
    def _persist_last_inputs(self, user_input: dict) -> None:
        self.hass.data[f"{DOMAIN}_last_url"] = user_input["url"]
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> GrentonWatcherOptionsFlowHandler:
        return GrentonWatcherOptionsFlowHandler()