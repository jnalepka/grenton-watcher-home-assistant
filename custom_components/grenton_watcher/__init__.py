import logging
import aiohttp
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)
DOMAIN = "grenton_watcher"

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    api_endpoint = entry.data["api_endpoint"]
    mappings = entry.options.get("mappings", [])

    entity_ids = list({m["entity_id"] for m in mappings})

    @callback
    async def state_changed(event):
        new_state = event.data.get("new_state")
        if not new_state:
            return

        payload = {}
        for m in mappings:
            if new_state.entity_id == m["entity_id"]:
                attr = m.get("attribute")
                value = new_state.state if attr == "state" else new_state.attributes.get(attr)
                payload[m["name"]] = value

        if not payload:
            return

        async with aiohttp.ClientSession() as session:
            try:
                _LOGGER.info("Grenton Watcher send payload: %s", payload)
                await session.post(api_endpoint, json=payload)
            except Exception as e:
                _LOGGER.error("Failed to send update: %s", e)

    remove_listener = async_track_state_change_event(hass, entity_ids, state_changed)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = remove_listener

    _LOGGER.info("Grenton Watcher started for mappings: %s", mappings)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    remove_listener = hass.data[DOMAIN].pop(entry.entry_id, None)
    if remove_listener:
        remove_listener()
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
