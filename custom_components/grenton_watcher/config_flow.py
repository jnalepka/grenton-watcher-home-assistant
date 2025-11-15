from homeassistant import config_entries
from homeassistant.helpers import selector
import voluptuous as vol
from .options_flow import GrentonWatcherOptionsFlowHandler

DOMAIN = "grenton_watcher"

class GrentonWatcherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data={
                    "url": user_input["url"],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("name"): str,
                vol.Required("url", default="http://192.168.0.4/HAlistener"): str,    # adres serwera
            }),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return GrentonWatcherOptionsFlowHandler()